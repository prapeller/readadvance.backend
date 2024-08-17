import fastapi as fa
import sqlalchemy as sa
from sqlalchemy import select

from core.constants import CELERY_TASK_PRIORITIES, PARTS_OF_SPEECH
from core.enums import ChatGPTModelsEnum, OrderEnum, UserWordStatusEnum, DBSessionModeEnum, TasksNamesEnum, \
    ResponseDetailEnum, LanguagesISO2NamesEnum, RequestMethodsEnum
from core.exceptions import AlreadyExistsException
from db.models.association import UserWordStatusFileAssoc
from db.models.file_storage import FileIndexModel
from db.models.word import WordModel
from db.serializers.analyses import AnalysesOutSerializer
from db.serializers.association import UserWordStatusFileCreateSerializer, UserWordStatusFileUpdateSerializer
from db.serializers.translations import TranslWordInSerializer, TranslWordOutSerializer, TranslNlpAPIInSerializer, \
    TranslNlpAPIOutSerializer
from db.serializers.word import WordCreateSerializer, WordUpdateSerializer, WordOrderByEnum, WordsPaginatedSerializer
from services.inter_service_manager.inter_service_manager import InterServiceManager
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_dependency, \
    sqlalchemy_repo_async_read_dependency
from services.translator.translator import translate_with_nlp_api
from services.word_manager.celery_tasks import words_identify_level_task
from services.word_manager.chatgpt_helpers import identify_word_level_chatgpt
from services.word_manager.logger_setup import logger


class WordManager:
    def __init__(self,
                 repo_write: SqlAlchemyRepositoryAsync,
                 repo_read: SqlAlchemyRepositoryAsync = None):
        self.repo_write = repo_write
        self.repo_read = repo_read

    async def _filter_query(self, query: sa.Select, word_params: dict) -> sa.Select:
        created_at = word_params.get('created_at')
        updated_at = word_params.get('updated_at')
        characters = word_params.get('characters')
        lemma = word_params.get('lemma')
        pos = word_params.get('pos')
        level_cefr_code = word_params.get('level_cefr_code')
        if characters is not None:
            assert len(characters.split(' ')) <= 1, 'only one word must be provided for search'
            query = query.filter(WordModel.characters.ilike(f'%{characters}%'))
        if lemma is not None:
            query = query.filter(WordModel.lemma.ilike(f'%{lemma}%'))
        if pos is not None:
            query = query.filter(WordModel.pos.ilike(f'%{pos}%'))
        if created_at is not None:
            query = query.filter(WordModel.created_at == created_at)
        if updated_at is not None:
            query = query.filter(WordModel.updated_at == updated_at)
        if level_cefr_code is not None:
            query = query.filter(WordModel.level_cefr_code == level_cefr_code)
        return query

    async def _paginate_query(
            self,
            stmt: sa.Select,
            order_by: WordOrderByEnum,
            order: OrderEnum,
            pagination_params: dict,
    ) -> sa.Select:
        order = sa.desc if order == OrderEnum.desc else sa.asc
        stmt = stmt.order_by(order(getattr(WordModel, order_by)))
        stmt = stmt.offset(pagination_params["offset"]).limit(pagination_params["limit"])
        return stmt

    async def get_word(self,
                       uuid: str,
                       session_mode: DBSessionModeEnum = DBSessionModeEnum.r,
                       raise_if_not_found=True,
                       ) -> WordModel:

        if session_mode == DBSessionModeEnum.r:
            assert self.repo_read is not None, 'repo_read must be provided'
            word = await self.repo_read.get(WordModel, raise_if_not_found=raise_if_not_found, uuid=uuid)
        else:
            word = await self.repo_write.get(WordModel, raise_if_not_found=raise_if_not_found, uuid=uuid)
        return word

    async def list_filtered_paginated_words(self,
                                            word_params: dict,
                                            pagination_params: dict,
                                            order_by: WordOrderByEnum,
                                            order: OrderEnum,
                                            base_query=None,
                                            ) -> WordsPaginatedSerializer:
        """list all words for particular language"""
        assert self.repo_read is not None, 'repo_read must be provided'

        language_iso_2 = word_params.get('language_iso_2')

        query = base_query if base_query is not None else select(WordModel).filter_by(language_iso_2=language_iso_2)

        total_count_result = await self.repo_read.session.execute(
            select(sa.func.count()).select_from(query.subquery())
        )
        total_count = total_count_result.scalar()

        query = await self._filter_query(query, word_params)

        filtered_count_result = await self.repo_read.session.execute(
            select(sa.func.count()).select_from(query.subquery()))
        filtered_count = filtered_count_result.scalar()

        query = await self._paginate_query(query, order_by, order, pagination_params)
        result = await self.repo_read.session.execute(query)
        words = list(result.scalars().all())

        return WordsPaginatedSerializer(
            words=words,
            total_count=total_count,
            filtered_count=filtered_count)

    async def list_filtered_paginated_users_words_by_status(self,
                                                            user_uuid: str,
                                                            word_params: dict,
                                                            pagination_params: dict,
                                                            order_by: WordOrderByEnum,
                                                            order: OrderEnum,
                                                            status: UserWordStatusEnum,
                                                            ) -> WordsPaginatedSerializer:
        """list words of user with particular language"""
        query = (
            select(WordModel)
            .filter_by(language_iso_2=word_params.get('language_iso_2'))
            .join(UserWordStatusFileAssoc)
            .filter(sa.and_(UserWordStatusFileAssoc.user_uuid == user_uuid,
                            UserWordStatusFileAssoc.status == status))
        )
        return await self.list_filtered_paginated_words(word_params, pagination_params, order_by, order, query)

    async def analyze_word_with_nlp_api(
            self,
            characters: str,
            iso2: LanguagesISO2NamesEnum,
    ) -> AnalysesOutSerializer:

        inter_serv_manager = InterServiceManager()
        url, code, resp = await inter_serv_manager.send_request_to_nlp(RequestMethodsEnum.post, 'analyses/analyze',
                                                                       {'content': characters, 'iso2': iso2})
        an_res = AnalysesOutSerializer.model_validate_json(resp)
        return an_res

    async def create_word(
            self,
            word_ser: WordCreateSerializer,
            gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4o,
    ):
        word = await self.repo_write.get(WordModel, characters=word_ser.characters,
                                         language_iso_2=word_ser.language_iso_2)
        if word is not None:
            raise AlreadyExistsException
        else:
            an_res = await self.analyze_word_with_nlp_api(word_ser.characters, word_ser.language_iso_2)
            word_res = an_res.words[0]
            word_ser.lemma = word_res['lemma']
            word_ser.pos = PARTS_OF_SPEECH[word_ser.language_iso_2][word_res['pos']]
            word = await self.repo_write.create(WordModel, word_ser)

            logger.debug(f'Created {word=}, starting celery {TasksNamesEnum.words_identify_level_task}...')

            words_identify_level_task.apply_async(
                args=[word.uuid, gpt_model],
                queue='default',
                priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.words_identify_level_task]
            )
            return word

    async def get_or_create_word(
            self,
            word_ser: WordCreateSerializer,
            gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4o,
    ) -> tuple[bool, WordModel]:
        is_created = False
        word = await self.repo_write.get(WordModel, characters=word_ser.characters,
                                         language_iso_2=word_ser.language_iso_2)
        if word is None:
            an_res = await self.analyze_word_with_nlp_api(word_ser.characters, word_ser.language_iso_2)
            word_res = an_res.words[0]
            word_ser.lemma = word_res['lemma']
            word_ser.pos = PARTS_OF_SPEECH[word_ser.language_iso_2][word_res['pos']]
            word = await self.repo_write.create(WordModel, word_ser)
            is_created = True

            logger.debug(f'Created {word=}, starting celery {TasksNamesEnum.words_identify_level_task}...')

            words_identify_level_task.apply_async(
                args=[word.uuid, gpt_model],
                queue='default',
                priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.words_identify_level_task]
            )
        return is_created, word

    async def update_word(self, word_uuid: str, word_ser: WordUpdateSerializer,
                          exclude_none=True, exclude_unset=True) -> WordModel:
        word = await self.repo_write.get(WordModel, raise_if_not_found=True, uuid=word_uuid)
        word = await self.repo_write.update(word, word_ser, exclude_none=exclude_none, exclude_unset=exclude_unset)
        logger.debug(f'updated {word=}')
        return word

    async def remove_word(self, word_uuid):
        res = await self.repo_write.remove_by_uuid(WordModel, word_uuid)
        logger.debug(f'removed {word_uuid=}')
        return res

    async def identify_word_level_with_chatgpt(self, word_uuid: str, gpt_model: ChatGPTModelsEnum) -> WordModel:
        word = await self.get_word(word_uuid, session_mode=DBSessionModeEnum.rw)
        level_cefr_code = await identify_word_level_chatgpt(word.characters, word.language_iso_2, gpt_model)
        word = await self.repo_write.update(word, WordUpdateSerializer(level_cefr_code=level_cefr_code))
        logger.debug(f'updated {word=} level to {level_cefr_code=}')
        return word

    async def add_to_users_words_with_status(self,
                                             user_uuid: str,
                                             word_uuid: str,
                                             status: UserWordStatusEnum,
                                             ) -> dict:
        """add word to user_word_status_file if not exists, or update status"""

        assoc = await self.repo_write.get(UserWordStatusFileAssoc, word_uuid=word_uuid, user_uuid=user_uuid)
        if assoc is None:
            await self.repo_write.create(UserWordStatusFileAssoc,
                                         UserWordStatusFileCreateSerializer(word_uuid=word_uuid,
                                                                            user_uuid=user_uuid,
                                                                            status=status))
        else:
            await self.repo_write.update(assoc, UserWordStatusFileUpdateSerializer(status=status))
        return {"detail": ResponseDetailEnum.ok}

    async def get_analyzed_word_translation_with_nlp_api(
            self,
            word_transl_in_ser: TranslWordInSerializer,
    ) -> TranslWordOutSerializer:

        word_image_file_index_uuid = None

        word_transl_out: TranslNlpAPIOutSerializer = await translate_with_nlp_api(
            TranslNlpAPIInSerializer(text_input=word_transl_in_ser.word_input,
                                     input_lang_iso2=word_transl_in_ser.input_lang_iso2,
                                     target_lang_iso2=word_transl_in_ser.target_lang_iso2))
        word_output = word_transl_out.text_output

        an_res: AnalysesOutSerializer = await self.analyze_word_with_nlp_api(characters=word_transl_in_ser.word_input,
                                                                             iso2=word_transl_in_ser.input_lang_iso2)
        word_pos = PARTS_OF_SPEECH[word_transl_in_ser.input_lang_iso2][an_res.words[0]['pos']]
        lemma = an_res.words[0]['lemma']
        lemma_word = await self.repo_write.get(WordModel, pos=word_pos, characters=lemma)
        if lemma_word is None:
            lemma_word = await self.create_word(WordCreateSerializer(
                characters=lemma, lemma=lemma, pos=word_pos, language_iso_2=word_transl_in_ser.input_lang_iso2
            ))

        word_image_assoc = await self.repo_write.get(UserWordStatusFileAssoc, user_uuid=None, word_uuid=lemma_word.uuid)
        if word_image_assoc is not None:
            word_image_file_index = await self.repo_write.get(FileIndexModel, uuid=word_image_assoc.file_index_uuid)
            if word_image_file_index is not None:
                word_image_file_index_uuid = word_image_file_index.uuid

        context_transl_out: TranslNlpAPIOutSerializer = await translate_with_nlp_api(
            TranslNlpAPIInSerializer(text_input=word_transl_in_ser.context_input,
                                     input_lang_iso2=word_transl_in_ser.input_lang_iso2,
                                     target_lang_iso2=word_transl_in_ser.target_lang_iso2)
        )
        context_output = context_transl_out.text_output

        return TranslWordOutSerializer(
            word_input=word_transl_in_ser.word_input,
            word_output=word_output,
            word_pos=word_pos,
            context_output=context_output,
            input_lang_iso2=word_transl_in_ser.input_lang_iso2,
            target_lang_iso2=word_transl_in_ser.target_lang_iso2,
            lemma_word=lemma_word,
            word_image_file_index_uuid=word_image_file_index_uuid,
        )


async def word_manager_dependency(
        repo_write: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        repo_read: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency)) -> WordManager:
    return WordManager(repo_write=repo_write, repo_read=repo_read)
