import fastapi as fa
import sqlalchemy as sa
from sqlalchemy import select

from core.constants import CELERY_TASK_PRIORITIES
from core.enums import ChatGPTModelsEnum, OrderEnum, UserWordStatusEnum, DBSessionModeEnum, TasksNamesEnum, \
    ResponseDetailEnum
from core.exceptions import AlreadyExistsException
from db.models.association import UserWordStatusFileAssoc
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.models.word import WordModel
from db.serializers.association import UserWordStatusFileCreateSerializer, UserWordStatusFileUpdateSerializer
from db.serializers.word import WordCreateSerializer, WordUpdateSerializer, WordOrderByEnum, WordsPaginatedSerializer
from services.chatgpt.word_identifier import get_word_level_chatgpt
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_dependency, \
    sqlalchemy_repo_async_read_dependency
from services.word_manager.celery_tasks import words_identify_level_task
from services.word_manager.logger_setup import logger


class WordManager:
    def __init__(self,
                 repo_write: SqlAlchemyRepositoryAsync,
                 repo_read: SqlAlchemyRepositoryAsync = None):
        self.repo_write = repo_write
        self.repo_read = repo_read

    async def _filter_query(self, query: sa.Select, word_params: dict) -> sa.Select:
        characters = word_params.get('characters')
        created_at = word_params.get('created_at')
        updated_at = word_params.get('updated_at')
        level_uuid = word_params.get('level_uuid')
        if characters is not None:
            query = query.filter(WordModel.characters.ilike(f'%{characters}%'))
        if created_at is not None:
            query = query.filter(WordModel.created_at == created_at)
        if updated_at is not None:
            query = query.filter(WordModel.updated_at == updated_at)
        if level_uuid is not None:
            query = query.filter(WordModel.level_uuid == level_uuid)
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

        query = base_query if base_query is not None else select(WordModel).filter_by(
            language_uuid=word_params.get('language_uuid'))

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
            .filter_by(language_uuid=word_params.get('language_uuid'))
            .join(UserWordStatusFileAssoc)
            .filter(sa.and_(UserWordStatusFileAssoc.user_uuid == user_uuid,
                            UserWordStatusFileAssoc.status == status))
        )
        return await self.list_filtered_paginated_words(word_params, pagination_params, order_by, order, query)

    async def create_word(self,
                          word_ser: WordCreateSerializer,
                          gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
        is_created, word = await self.repo_write.get_or_create(WordModel, word_ser)
        if not is_created:
            raise AlreadyExistsException(f'this word already exists in this language')
        logger.debug(f'Created {word=}, starting celery {TasksNamesEnum.words_identify_level_task}...')

        words_identify_level_task.apply_async(
            args=[word.uuid, gpt_model],
            queue='default',
            priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.words_identify_level_task]
        )
        return word

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

    async def identify_word_level(self, word: WordModel, gpt_model: ChatGPTModelsEnum) -> WordModel:
        language = await self.repo_write.get(LanguageModel, uuid=word.language_uuid)
        level_code = await get_word_level_chatgpt(word.characters, language.iso2, gpt_model)
        level = await self.repo_write.get(LevelModel, cefr_code=level_code)
        word = await self.repo_write.update(word, WordUpdateSerializer(level_uuid=level.uuid))
        logger.debug(f'updated {word=} level to {level=}')
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


async def word_manager_dependency(
        repo_write: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        repo_read: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency)) -> WordManager:
    return WordManager(repo_write=repo_write, repo_read=repo_read)
