import abc
import typing
from pathlib import Path
from typing import Type, Any

import fastapi as fa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as pd_Model
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.orm.query import Query

from core.enums import ResponseDetailEnum
from core.exceptions import BadRequestException, AlreadyExistsException, NotFoundException
from core.logger_config import setup_logger
from db import (
    SessionLocalSync,
    SessionLocalAsync, SessionLocalObjStorageAsync, SessionLocalObjStorageSync, SessionLocalReadSync,
    SessionLocalReadAsync,
)
from db.models.association import WordFileUserStatusAssoc
from db.models.file_storage import FileStorageModel, FileIndexModel
from db.models.grammar import GrammarModel
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.models.phrase import PhraseModel
from db.models.readstash_text import TextModel
from db.models.user import UserModel
from db.models.word import WordModel

sa_Model = typing.Union[
    WordFileUserStatusAssoc,
    FileStorageModel, FileIndexModel,
    GrammarModel,
    LanguageModel,
    LevelModel,
    PhraseModel,
    TextModel,
    UserModel,
    WordModel,
]

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, Model, serializer):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, Model, **kwargs) -> sa_Model:
        raise NotImplementedError


def my_jsonable_encoder(obj: Any, exclude_none: bool = False, exclude_unset: bool = False) -> Any:
    if isinstance(obj, pd_Model):
        obj_dict = obj.model_dump(exclude_none=exclude_none, exclude_unset=exclude_unset)
        return {key: my_jsonable_encoder(value, exclude_none=exclude_none, exclude_unset=exclude_unset) for
                key, value in obj_dict.items()}
    elif isinstance(obj, bytes):
        return obj
    elif isinstance(obj, list):
        return [my_jsonable_encoder(item, exclude_none=exclude_none, exclude_unset=exclude_unset) for item in obj]
    elif isinstance(obj, dict):
        return {key: my_jsonable_encoder(value, exclude_none=exclude_none, exclude_unset=exclude_unset) for key, value
                in obj.items()}
    else:
        return jsonable_encoder(obj, exclude_none=exclude_none, exclude_unset=exclude_unset)


class SqlAlchemyRepositorySync(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def _try_commit_session(self):
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    def _try_add_commit_refresh(self, obj):
        self.session.add(obj)
        self._try_commit_session()
        self.session.refresh(obj)
        return obj

    def _try_delete(self, Model, obj):
        if obj is None:
            raise NotFoundException(f"{Model} {id=:} not found.")
        self.session.delete(obj)
        self._try_commit_session()

    def _try_delete_many(self, objs):
        for obj in objs:
            self.session.delete(obj)
        self._try_commit_session()

    @staticmethod
    def _get_serializer_data(serializer: pd_Model | dict, exclude_none: bool, exclude_unset: bool) -> dict:
        if isinstance(serializer, dict):
            serializer_data = serializer
        else:
            serializer_data = my_jsonable_encoder(serializer, exclude_none=exclude_none, exclude_unset=exclude_unset)
        return serializer_data

    def create(self, Model: Type[sa_Model], serializer: pd_Model | dict,
               exclude_none=True, exclude_unset=True) -> sa_Model:
        serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)
        existing_obj = self.session.query(Model).filter_by(**serializer_data).first()
        if existing_obj is not None:
            raise AlreadyExistsException
        obj = Model(**serializer_data)
        obj = self._try_add_commit_refresh(obj)
        return obj

    def get(self, Model: Type[sa_Model], **kwargs) -> sa_Model:
        obj = self.session.query(Model).filter_by(**kwargs).first()
        if obj is None:
            raise NotFoundException(f"{Model=:} not found")
        return obj

    def get_many_by_id_list(self, Model: Type[sa_Model], id_list: list[int]) -> list[sa_Model]:
        """getting objs one by one and if cant find any of them, raises 404"""
        objs = []
        for id in id_list:
            obj = self.session.query(Model).get(id)
            if obj is None:
                raise NotFoundException(f"{Model} {id=:} not found.")
            objs.append(obj)
        return objs

    def get_many_by_uuid_list(self, Model: Type[sa_Model], uuid_list: list[str]) -> list[sa_Model]:
        """getting objs one by one and if cant find any of them, raises 404"""
        objs = []
        for _uuid in uuid_list:
            obj = self.get(Model, uuid=_uuid)
            if obj is None:
                raise NotFoundException(f"{Model} {_uuid=:} not found.")
            objs.append(obj)
        return objs

    def get_all(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).all()

    def get_all_active(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).filter(Model.is_active == True).all()

    def get_all_inactive(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).filter(Model.is_active == False).all()

    def get_query(self, Model: Type[sa_Model], **kwargs) -> Query:
        query = self.session.query(Model)
        for attr, value in kwargs.items():
            query = query.filter(Model.__dict__.get(attr) == value)
        return query

    def get_query_all_active(self, Model: Type[sa_Model], **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=True, **kwargs)

    def get_query_all_inactive(self, Model: Type[sa_Model], **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=False, **kwargs)

    def get_or_create(self, Model: Type[sa_Model], serializer: pd_Model | dict,
                      exclude_none=True, exclude_unset=True) -> tuple[bool, sa_Model]:
        serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)
        is_created = False
        obj = self.session.query(Model).filter_by(**serializer_data).first()
        if obj is None:
            obj = Model(**serializer_data)
            obj = self._try_add_commit_refresh(obj)
            is_created = True
        return is_created, obj

    def create_many(self, Model: Type[sa_Model], serializers: list[pd_Model | dict],
                    exclude_none=True, exclude_unset=True) -> list[sa_Model]:
        objs = []
        for serializer in serializers:
            serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)
            obj = Model(**serializer_data)
            self.session.add(obj)
            objs.append(obj)
        self._try_commit_session()
        return objs

    def get_or_create_many(self, Model: Type[sa_Model], serializers: list[pd_Model | dict],
                           exclude_none=True, exclude_unset=True) -> list[sa_Model]:
        objs = []
        for serializer in serializers:
            serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)
            obj = self.session.query(Model).filter_by(**serializer_data).first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        self._try_commit_session()
        return objs

    def update(self, obj: sa_Model, serializer: pd_Model | dict,
               exclude_none=True, exclude_unset=True) -> sa_Model:
        serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)

        fields_to_update = [x for x in serializer_data if hasattr(obj, x)]
        for field in fields_to_update:
            setattr(obj, field, serializer_data[field])

        obj = self._try_add_commit_refresh(obj)
        return obj

    def update_many(self, objs: list[sa_Model], serializer: pd_Model | dict,
                    exclude_none=True, exclude_unset=True) -> list[sa_Model]:
        serializer_data = self._get_serializer_data(serializer, exclude_none, exclude_unset)
        for obj in objs:
            fields_to_update = [x for x in serializer_data if hasattr(obj, x)]
            for field in fields_to_update:
                setattr(obj, field, serializer_data[field])
            self.session.add(obj)
        self._try_commit_session()
        return objs

    def remove(self, Model: Type[sa_Model], id: int) -> dict:
        obj = self.session.query(Model).get(id)
        self._try_delete(Model, obj)
        return {"detail": ResponseDetailEnum.ok}

    def remove_by_uuid(self, Model: Type[sa_Model], _uuid: str) -> dict:
        obj = self.get(Model, uuid=_uuid)
        self._try_delete(Model, obj)
        return {"detail": ResponseDetailEnum.ok}

    def remove_many_by_id_list(self, Model: Type[sa_Model], id_list: list[int]) -> dict:
        """remove objects if found them"""
        objs = self.session.query(Model).filter(Model.id.in_(id_list)).all()
        self._try_delete_many(objs)
        return {"detail": ResponseDetailEnum.ok}

    def remove_many_by_uuid_list(self, Model: Type[sa_Model], uuid_list: list[str]) -> dict:
        """remove objects if found them"""
        objs = self.session.query(Model).filter(Model.uuid.in_(uuid_list)).all()
        self._try_delete_many(objs)
        return {"detail": ResponseDetailEnum.ok}


class SqlAlchemyRepositoryAsync(AbstractRepository):
    def __init__(self, session: sa_async.AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def create(self, Model: type[sa_Model], serializer) -> sa_Model:
        serializer_data = serializer.model_dump(exclude_unset=True)
        obj = Model(**serializer_data)
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

        await self.session.refresh(obj)
        return obj

    async def get(self, Model: type[sa_Model], raise_if_not_found=False, **kwargs) -> sa_Model | None:
        stmt = select(Model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if raise_if_not_found:
            if obj is None:
                raise NotFoundException(f"{Model} not found")
        return obj

    async def list_filtered(self, Model: type[sa_Model], exclude_none: bool = True, **kwargs) -> list[sa_Model]:
        kwargs_local = kwargs.copy()
        if exclude_none:
            for k, v in kwargs.items():
                if v is None:
                    kwargs_local.pop(k)
        stmt = select(Model).filter_by(**kwargs_local)
        result = await self.session.execute(stmt)
        objs = list(result.scalars().all())
        return objs

    async def get_or_create_many(
            self, Model: type[sa_Model], serializers: list[pd_Model]
    ) -> list[sa_Model]:
        objs = []
        for serializer in serializers:
            serializer_data = my_jsonable_encoder(serializer)
            stmt = select(Model).filter_by(**serializer_data)
            result = await self.session.execute(stmt)
            obj = result.scalars().first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        return objs

    async def get_or_create_by_name(self, Model: type[sa_Model], name: str) -> tuple[bool, sa_Model]:
        is_created = False
        stmt = select(Model).filter_by(name=name)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if not obj:
            obj = Model(name=name)
            self.session.add(obj)
            try:
                await self.session.commit()
            except IntegrityError as e:
                await self.session.rollback()
                detail = str(e)
                logger.error(detail)
                raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
            await self.session.refresh(obj)
            is_created = True
        return is_created, obj

    async def get_or_create(self, Model: type[sa_Model], serializer: pd_Model) -> tuple[bool, sa_Model]:
        is_created = False
        stmt = select(Model).filter_by(**serializer.model_dump())
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if not obj:
            obj = Model(**serializer.model_dump())
            self.session.add(obj)
            try:
                await self.session.commit()
            except IntegrityError as e:
                await self.session.rollback()
                detail = str(e)
                logger.error(detail)
                raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
            await self.session.refresh(obj)
            is_created = True
        return is_created, obj

    async def update(self, obj: sa_Model, serializer: pd_Model | dict, exclude_unset=True,
                     exclude_none=True) -> sa_Model:
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none)

        # Filter out fields that should not be updated
        fields_to_update = [x for x in update_data if hasattr(obj, x)]
        for field in fields_to_update:
            setattr(obj, field, update_data[field])
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        await self.session.refresh(obj)
        return obj

    async def remove(self, Model: type[sa_Model], id) -> dict:
        obj = await self.get(Model, id=id)
        if obj is None:
            raise BadRequestException(f'Cant remove, {Model=:} {id=:} not found')
        await self.session.delete(obj)
        try:
            await self.session.commit()
            return {"detail": ResponseDetailEnum.ok}
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    async def remove_by_uuid(self, Model: type[sa_Model], uuid: str) -> dict:
        obj = await self.get(Model, uuid=uuid)
        if obj is None:
            raise BadRequestException(f'Cant remove, {Model=:} {uuid=:} not found')
        await self.session.delete(obj)
        try:
            await self.session.commit()
            return {"detail": ResponseDetailEnum.ok}
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e)
            logger.error(detail)
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# WRITE DEPENDENCIES

# sync
def sqlalchemy_repo_sync_dependency() -> SqlAlchemyRepositorySync:
    session = SessionLocalSync()
    repo = SqlAlchemyRepositorySync(session)
    try:
        yield repo
    finally:
        session.close()


def sqlalchemy_repo_obj_storage_sync_dependency() -> SqlAlchemyRepositorySync:
    session = SessionLocalObjStorageSync()
    repo = SqlAlchemyRepositorySync(session)
    try:
        yield repo
    finally:
        session.close()


# async
async def sqlalchemy_repo_async_dependency() -> SqlAlchemyRepositoryAsync:
    try:
        async with SessionLocalAsync() as session:
            repo = SqlAlchemyRepositoryAsync(session)
            yield repo
    finally:
        await session.close()


async def sqlalchemy_repo_obj_storage_async_dependency() -> SqlAlchemyRepositoryAsync:
    try:
        async with SessionLocalObjStorageAsync() as session:
            repo = SqlAlchemyRepositoryAsync(session)
            yield repo
    finally:
        await session.close()


# READ DEPENDENCIES

# sync
def sqlalchemy_repo_sync_read_dependency() -> SqlAlchemyRepositorySync:
    session_read = SessionLocalReadSync()
    repo = SqlAlchemyRepositorySync(session_read)
    try:
        yield repo
    finally:
        session_read.close()


def sqlalchemy_repo_obj_storage_sync_read_dependency() -> SqlAlchemyRepositorySync:
    session_read = SessionLocalObjStorageSync()
    repo = SqlAlchemyRepositorySync(session_read)
    try:
        yield repo
    finally:
        session_read.close()


# async
async def sqlalchemy_repo_async_read_dependency() -> SqlAlchemyRepositoryAsync:
    try:
        async with SessionLocalReadAsync() as session_read:
            repo = SqlAlchemyRepositoryAsync(session_read)
            yield repo
    finally:
        await session_read.close()


async def sqlalchemy_repo_obj_storage_async_read_dependency() -> SqlAlchemyRepositoryAsync:
    try:
        async with SessionLocalObjStorageAsync() as session_read:
            repo = SqlAlchemyRepositoryAsync(session_read)
            yield repo
    finally:
        await session_read.close()
