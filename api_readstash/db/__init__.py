import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings, POSTGRES_DEBUG


def init_models():
    from db.models import association  # noqa
    from db.models import file_storage  # noqa
    from db.models import grammar  # noqa
    from db.models import language  # noqa
    from db.models import level  # noqa
    from db.models import phrase  # noqa
    from db.models import text  # noqa
    from db.models import user  # noqa
    from db.models import word  # noqa
    from db.models import periodic_task  # noqa


# postgres_readstash

# write
POSTGRES_READSTASH_URL_POSTFIX = (
    f'{settings.POSTGRES_READSTASH_USER}:{settings.POSTGRES_READSTASH_PASSWORD}@'
    f'{settings.POSTGRES_READSTASH_HOST}:{settings.POSTGRES_READSTASH_PORT}/{settings.POSTGRES_READSTASH_DB}')

POSTGRES_READSTASH_URL_SYNC = f'postgresql+psycopg2://{POSTGRES_READSTASH_URL_POSTFIX}'
engine_sync = create_engine(POSTGRES_READSTASH_URL_SYNC, pool_pre_ping=True)
SessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

POSTGRES_READSTASH_URL_ASYNC = f'postgresql+asyncpg://{POSTGRES_READSTASH_URL_POSTFIX}'
engine_async = create_async_engine(POSTGRES_READSTASH_URL_ASYNC, future=True)
SessionLocalAsync = sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)  # noqa

# read
POSTGRES_READSTASH_READ_URL_POSTFIX = (
    f'{settings.POSTGRES_READSTASH_READ_USER}:{settings.POSTGRES_READSTASH_READ_PASSWORD}@'
    f'{settings.POSTGRES_READSTASH_READ_HOST}:{settings.POSTGRES_READSTASH_READ_PORT}/{settings.POSTGRES_READSTASH_READ_DB}')

POSTGRES_READSTASH_READ_URL_SYNC = f'postgresql+psycopg2://{POSTGRES_READSTASH_READ_URL_POSTFIX}'
engine_read_sync = create_engine(POSTGRES_READSTASH_READ_URL_SYNC, pool_pre_ping=True)
SessionLocalReadSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_read_sync)

POSTGRES_READSTASH_READ_URL_ASYNC = f'postgresql+asyncpg://{POSTGRES_READSTASH_READ_URL_POSTFIX}'
engine_read_async = create_async_engine(POSTGRES_READSTASH_READ_URL_ASYNC, future=True)
SessionLocalReadAsync = sessionmaker(engine_read_async, class_=AsyncSession, expire_on_commit=False)  # noqa

# postgres_obj_storage

# write
POSTGRES_OBJ_STORAGE_URL_POSTFIX = (
    f'{settings.POSTGRES_OBJECT_STORAGE_USER}:{settings.POSTGRES_OBJECT_STORAGE_PASSWORD}@'
    f'{settings.POSTGRES_OBJECT_STORAGE_HOST}:{settings.POSTGRES_OBJECT_STORAGE_PORT}/'
    f'{settings.POSTGRES_OBJECT_STORAGE_DB}')

POSTGRES_OBJ_STORAGE_URL_SYNC = f'postgresql+psycopg2://{POSTGRES_OBJ_STORAGE_URL_POSTFIX}'
engine_obj_storage_sync = create_engine(POSTGRES_OBJ_STORAGE_URL_SYNC, pool_pre_ping=True)
SessionLocalObjStorageSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_obj_storage_sync)

POSTGRES_OBJ_STORAGE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_OBJ_STORAGE_URL_POSTFIX}"
engine_obj_storage_async = create_async_engine(POSTGRES_OBJ_STORAGE_URL_ASYNC, future=True)
SessionLocalObjStorageAsync = sessionmaker(engine_obj_storage_async, class_=AsyncSession,  # noqa
                                           expire_on_commit=False)

# read
POSTGRES_OBJ_STORAGE_READ_URL_POSTFIX = (
    f'{settings.POSTGRES_OBJECT_STORAGE_READ_USER}:{settings.POSTGRES_OBJECT_STORAGE_READ_PASSWORD}@'
    f'{settings.POSTGRES_OBJECT_STORAGE_READ_HOST}:{settings.POSTGRES_OBJECT_STORAGE_READ_PORT}/'
    f'{settings.POSTGRES_OBJECT_STORAGE_READ_DB}')

POSTGRES_OBJ_STORAGE_READ_URL_SYNC = f'postgresql+psycopg2://{POSTGRES_OBJ_STORAGE_READ_URL_POSTFIX}'
engine_obj_storage_read_sync = create_engine(POSTGRES_OBJ_STORAGE_READ_URL_SYNC, pool_pre_ping=True)
SessionLocalObjStorageReadSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_obj_storage_read_sync)

POSTGRES_OBJ_STORAGE_READ_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_OBJ_STORAGE_READ_URL_POSTFIX}"
engine_obj_storage_read_async = create_async_engine(POSTGRES_OBJ_STORAGE_READ_URL_ASYNC, future=True)
SessionLocalObjStorageReadAsync = sessionmaker(engine_obj_storage_read_async, class_=AsyncSession,  # noqa
                                               expire_on_commit=False)

Base = declarative_base()
BaseObjStorage = declarative_base()

logging.basicConfig()
logging_level = logging.INFO if POSTGRES_DEBUG == True else logging.ERROR
logging.getLogger('sqlalchemy.engine').setLevel(logging_level)
