import datetime as dt

import pydantic as pd


class FileStorageUpdateSerializer(pd.BaseModel):
    file_data: bytes


class FileStorageCreateSerializer(pd.BaseModel):
    file_data: bytes


class FileStorageReadAsyncCachedSerializer(pd.BaseModel):
    file_data: bytes
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        from_attributes = True


class FileIndexUpdateSerializer(pd.BaseModel):
    name: str | None = None
    content_type: str | None = None


class FileIndexCreateSerializer(FileIndexUpdateSerializer):
    name: str | None = None
    content_type: str | None = None

    file_storage_uuid: str | None = None


class FileIndexReadSerializer(FileIndexCreateSerializer):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    name: str
    content_type: str

    # file_storage.uuid (uuid from another db, not db-driven reference,
    # will need to maintain referencing manually)
    file_storage_uuid: str

    class Config:
        from_attributes = True


class FileIndexReadAsyncCachedSerializer(pd.BaseModel):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    name: str
    content_type: str

    file_storage_uuid: str

    class Config:
        from_attributes = True
