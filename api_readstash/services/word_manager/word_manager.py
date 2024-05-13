from pathlib import Path

import fastapi as fa
import sqlalchemy as sa
from sqlalchemy import select

from core.enums import ChatGPTModelsEnum, LevelSystemNamesEnum, OrderEnum, UserWordStatusEnum, ResponseDetailEnum, \
    LanguagesISO2NamesEnum, DBSessionModeEnum
from core.exceptions import AlreadyExistsException, NotFoundException
from core.logger_config import setup_logger
from db.models.association import WordFileUserStatusAssoc
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.models.word import WordModel
from db.serializers.association import WordFileUserStatusCreateSerializer, WordFileUserStatusUpdateSerializer
from db.serializers.word import WordCreateSerializer, WordUpdateSerializer, WordOrderByEnum, WordsPaginatedSerializer
from services.chatgpt.cefr_identifier import get_word_level_chatgpt
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_dependency, \
    sqlalchemy_repo_async_read_dependency

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class WordManager():
    def __init__(self,
                 repo_write: SqlAlchemyRepositoryAsync,
                 repo_read: SqlAlchemyRepositoryAsync):
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

    async def _word_exists(self, word_ser: WordCreateSerializer) -> bool:
        assert word_ser.characters is not None, 'characters must be provided'
        assert word_ser.language_uuid is not None, 'language must be provided'
        word = await self.repo_write.get(WordModel, characters=word_ser.characters,
                                         language_uuid=word_ser.language_uuid)
        return word is not None

    async def _raise_if_word_exists(self, word_ser: WordCreateSerializer | WordUpdateSerializer) -> None:
        if await self._word_exists(word_ser):
            raise AlreadyExistsException(detail=f'Word "{word_ser.characters}" in this language already exists')

    async def get_word(self,
                       uuid: str,
                       session_mode: DBSessionModeEnum = DBSessionModeEnum.r,
                       ) -> WordModel:
        if session_mode == DBSessionModeEnum.r:
            word = await self.repo_read.get(WordModel, uuid=uuid)
        else:
            word = await self.repo_write.get(WordModel, uuid=uuid)
        if word is None:
            raise NotFoundException(detail='Word not found')
        return word

    async def list_filtered_paginated(self,
                                      word_params: dict,
                                      pagination_params: dict,
                                      order_by: WordOrderByEnum,
                                      order: OrderEnum,
                                      base_query=None,
                                      ) -> WordsPaginatedSerializer:
        """list all words for particular language"""
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

    async def list_users_words(self,
                               user_uuid: str,
                               word_params: dict,
                               pagination_params: dict,
                               order_by: WordOrderByEnum,
                               order: OrderEnum,
                               status: UserWordStatusEnum,
                               ) -> WordsPaginatedSerializer:
        """list all words for particular language"""
        query = (
            select(WordModel)
            .filter_by(language_uuid=word_params.get('language_uuid'))
            .join(WordFileUserStatusAssoc)
            .filter(sa.and_(WordFileUserStatusAssoc.user_uuid == user_uuid,
                            WordFileUserStatusAssoc.status == status))
        )
        return await self.list_filtered_paginated(word_params, pagination_params, order_by, order, query)

    async def add_to_users_words_with_status(self,
                                             user_uuid: str,
                                             word_uuid: str,
                                             status: UserWordStatusEnum,
                                             ) -> dict:
        """add word to word_file_user_status if not exists, or update status"""

        word = await self.get_word(word_uuid)
        assoc = await self.repo_write.get(WordFileUserStatusAssoc, word_uuid=word_uuid, user_uuid=user_uuid)
        if assoc is None:
            await self.repo_write.create(WordFileUserStatusAssoc,
                                         WordFileUserStatusCreateSerializer(word_uuid=word_uuid,
                                                                            user_uuid=user_uuid,
                                                                            status=status))
        else:
            await self.repo_write.update(assoc, WordFileUserStatusUpdateSerializer(status=status))
        return {"detail": ResponseDetailEnum.ok}

    async def update_word_level(self,
                                word: WordModel,
                                gpt_model: ChatGPTModelsEnum,
                                ) -> WordModel:
        language = await self.repo_write.get(LanguageModel, uuid=word.language_uuid)
        language_iso2: LanguagesISO2NamesEnum = language.iso2  # noqa
        word_str, cefr_code, model = await get_word_level_chatgpt(word.characters, language_iso2, gpt_model,
                                                                  LevelSystemNamesEnum.CEFR)
        level = await self.repo_write.get(LevelModel, cefr_code=cefr_code, language_uuid=word.language_uuid)
        word = await self.repo_write.update(word, WordUpdateSerializer(level_uuid=level.uuid))
        return word

    async def create_word(self, gpt_model: ChatGPTModelsEnum, word_ser: WordCreateSerializer):
        await self._raise_if_word_exists(word_ser)
        word = await self.repo_write.create(WordModel, word_ser)
        word = await self.update_word_level(word, gpt_model)
        logger.debug(f'created {word=}')
        return word

    async def identify_word_level(self, word_uuid, gpt_model: ChatGPTModelsEnum) -> WordModel:
        word = await self.get_word(word_uuid, session_mode=DBSessionModeEnum.rw)
        word = await self.update_word_level(word, gpt_model)
        logger.debug(f'identified word level {word=}')
        return word

    async def update_word(self, word_uuid: str, word_ser: WordUpdateSerializer, exclude_none=True,
                          exclude_unset=True) -> WordModel:
        word = await self.repo_write.get(WordModel, uuid=word_uuid)
        if word is None:
            raise NotFoundException(detail='Word not found')

        if word_ser.characters is not None or word_ser.language is not None:
            await self._raise_if_word_exists(word_ser)

        word = await self.repo_write.update(word, word_ser, exclude_none=exclude_none, exclude_unset=exclude_unset)
        logger.debug(f'updated {word=}')
        return word

    async def remove_word(self, word_uuid):
        return await self.repo_write.remove_by_uuid(WordModel, word_uuid)


async def word_manager_dependency(
        repo_write: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        repo_read: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency)) -> WordManager:
    return WordManager(repo_write=repo_write, repo_read=repo_read)
