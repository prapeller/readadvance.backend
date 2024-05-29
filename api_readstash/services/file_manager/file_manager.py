import base64
from pathlib import Path
from urllib.parse import quote

import fastapi as fa

from core.exceptions import AlreadyExistsException
from core.logger_config import setup_logger
from db.models.file_storage import FileStorageModel, FileIndexModel
from db.serializers.file_storage import (
    FileIndexCreateSerializer,
    FileIndexUpdateSerializer,
    FileStorageCreateSerializer,
    FileStorageUpdateSerializer,
    FileStorageReadAsyncCachedSerializer,
    FileIndexReadAsyncCachedSerializer,
)
from services.cache.cache import RedisCache
from services.postgres.repository import (
    SqlAlchemyRepositorySync,
    SqlAlchemyRepositoryAsync,
    sqlalchemy_repo_sync_dependency,
    sqlalchemy_repo_async_dependency,
    sqlalchemy_repo_obj_storage_sync_dependency,
    sqlalchemy_repo_obj_storage_async_dependency,
)

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class FileManager():
    def __init__(self,
                 index_repo_sync: SqlAlchemyRepositorySync,
                 object_storage_repo_sync: SqlAlchemyRepositorySync,
                 index_repo_async: SqlAlchemyRepositoryAsync,
                 object_storage_repo_async: SqlAlchemyRepositoryAsync,
                 ):
        self.index_repo_sync = index_repo_sync
        self.object_storage_repo_sync = object_storage_repo_sync
        self.index_repo_async = index_repo_async
        self.object_storage_repo_async = object_storage_repo_async
        self.cache = RedisCache()

    def _raise_if_file_index_name_exists(self, file_name):
        file_index = self.index_repo_sync.session.query(FileIndexModel).filter_by(name=file_name).first()
        if file_index is not None:
            raise AlreadyExistsException(detail='file with this name already exists')

    async def create(self,
                     file_index_ser: FileIndexCreateSerializer,
                     file_storage_ser: FileStorageCreateSerializer,
                     ) -> FileIndexModel:

        self._raise_if_file_index_name_exists(file_index_ser.name)

        file_storage = None
        file_index = None

        try:
            file_storage = self.object_storage_repo_sync.create(FileStorageModel, file_storage_ser)
            file_index_ser.file_storage_uuid = file_storage.uuid
            file_index = self.index_repo_sync.create(FileIndexModel, file_index_ser)
            return file_index
        except Exception as e:
            if file_storage is not None:
                self.object_storage_repo_sync.remove_by_uuid(FileStorageModel, file_storage.uuid)
            if file_index is not None:
                self.index_repo_sync.remove_by_uuid(FileIndexModel, file_index.uuid)
            raise e

    async def get_file_storage(self, file_index_uuid: str) -> FileStorageModel:
        """get file_storage by file_index_uuid with async repos"""

        file_index = await self.index_repo_async.get(FileIndexModel, uuid=file_index_uuid)
        file_storage = await self.object_storage_repo_async.get(FileStorageModel, uuid=file_index.file_storage_uuid)
        return file_storage

    async def get(self, file_index_uuid: str) -> fa.responses.StreamingResponse:
        """get streamed file_starage.file_data with async repos"""

        file_index: FileIndexModel = await self.index_repo_async.get(FileIndexModel, uuid=file_index_uuid)
        file_storage = await self.object_storage_repo_async.get(FileStorageModel, uuid=file_index.file_storage_uuid)
        headers = {'Content-Disposition': f'attachment; filename*=UTF-8"{quote(file_index.name)}"',
                   'Content-Type': file_index.content_type}

        def file_data_generator():
            # Define chunk size (e.g., 10KB, 32KB, etc.)
            chunk_size = 32 * 1024  # 32KB
            for i in range(0, len(file_storage.file_data), chunk_size):
                yield file_storage.file_data[i:i + chunk_size]

        return fa.responses.StreamingResponse(content=file_data_generator(), headers=headers)

    async def get_cached(self, file_index_uuid: str) -> fa.responses.StreamingResponse:
        """get with async repos using cache"""

        # file_index: FileIndexModel = await self.index_repo_async.get(FileIndexModel, uuid=file_index_uuid)
        # file_storage = await self.object_storage_repo_async.get(FileStorageModel, uuid=file_index.file_storage_uuid)

        file_index_cache_key = f"file_index_uuid:{file_index_uuid}"
        file_index_dict = await self.cache.get_cache(file_index_cache_key)

        if file_index_dict is None:
            file_index: FileIndexModel = await self.index_repo_async.get(FileIndexModel, uuid=file_index_uuid)
            file_index_name = file_index.name
            file_index_content_type = file_index.content_type
            file_storage_uuid = file_index.file_storage_uuid
            file_index_dict = FileIndexReadAsyncCachedSerializer.model_validate(file_index).model_dump()
            await self.cache.set_cache(file_index_cache_key, file_index_dict)

        else:
            file_index_name = file_index_dict.get('name')
            file_index_content_type = file_index_dict.get('content_type')
            file_storage_uuid = file_index_dict.get('file_storage_uuid')

        file_storage_cache_key = f"file_storage_uuid:{file_storage_uuid}"
        file_storage_dict = await self.cache.get_cache(file_storage_cache_key)

        if file_storage_dict is None:
            file_storage: FileStorageModel = await self.object_storage_repo_async.get(FileStorageModel,
                                                                                      uuid=file_storage_uuid)
            file_storage_file_data = file_storage.file_data
            file_storage_dict = FileStorageReadAsyncCachedSerializer.model_validate(file_storage).model_dump()
            await self.cache.set_cache(file_storage_cache_key, file_storage_dict)
        else:
            file_storage_file_data = base64.b64decode(file_storage_dict.get('file_data'))

        headers = {'Content-Disposition': f'attachment; filename*=UTF-8"{quote(file_index_name)}"',
                   'Content-Type': file_index_content_type}

        def file_data_generator():
            # Define chunk size (e.g., 10KB, 32KB, etc.)
            chunk_size = 32 * 1024  # 32KB
            for i in range(0, len(file_storage_file_data), chunk_size):
                yield file_storage_file_data[i:i + chunk_size]

        return fa.responses.StreamingResponse(content=file_data_generator(), headers=headers)

    async def update(self, file_index_uuid: str, file_index_ser: FileIndexUpdateSerializer,
                     file: fa.UploadFile | None) -> FileIndexModel:
        """update with sync repos"""
        file_index = self.index_repo_sync.get(FileIndexModel, uuid=file_index_uuid)

        if file is not None:
            file_data = await file.read()
            file_storage_ser = FileStorageUpdateSerializer(file_data=file_data)
            file_storage = self.object_storage_repo_sync.get(FileStorageModel, uuid=file_index.file_storage_uuid)
            self.object_storage_repo_sync.update(file_storage, file_storage_ser)
        return self.index_repo_sync.update(file_index, file_index_ser)

    async def remove(self, file_uuid: str) -> None:
        """remove with sync repos"""
        file_index = self.index_repo_sync.get(FileIndexModel, uuid=file_uuid)
        self.object_storage_repo_sync.remove_by_uuid(FileStorageModel, file_index.file_storage_uuid)
        self.index_repo_sync.remove_by_uuid(FileIndexModel, file_uuid)


async def file_manager_dependency(
        index_repo_sync: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
        object_storage_repo_sync: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_obj_storage_sync_dependency),
        index_repo_async: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        object_storage_repo_async: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_obj_storage_async_dependency),
):
    return FileManager(
        index_repo_sync=index_repo_sync,
        object_storage_repo_sync=object_storage_repo_sync,
        index_repo_async=index_repo_async,
        object_storage_repo_async=object_storage_repo_async,
    )
