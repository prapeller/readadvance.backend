import argparse
import configparser
import os
import tempfile
from pathlib import Path

import sqlalchemy as sa
from alembic.config import Config

from core.config import BASE_DIR
from core.enums import DBEnum
from db import POSTGRES_READSTASH_URL_SYNC, POSTGRES_OBJ_STORAGE_URL_SYNC

ALEMBIC_PATH = BASE_DIR / 'alembic'
ALEMBIC_INI_PATH = BASE_DIR / 'alembic.ini'


def get_current_version(db: DBEnum):
    updated_config = get_updated_alembic_config(db)
    engine = sa.create_engine(next(updated_config).get_main_option('sqlalchemy.url'))
    connection = engine.connect()
    try:
        result = connection.execute(sa.text('select version_num from alembic_version'))
        row = result.fetchone()
        if row:
            current_version = row[0]
            return current_version
        return None
    finally:
        connection.close()
        engine.dispose()


def get_updated_alembic_config(db: DBEnum):
    # Read the alembic.ini file
    os.environ['TARGET_DB'] = db
    config = configparser.ConfigParser()
    config.read(ALEMBIC_INI_PATH)

    # Set the sqlalchemy.url, version_locations, script_location values
    if db == DBEnum.postgres_readstash:
        db_url = POSTGRES_READSTASH_URL_SYNC
    else:
        db_url = POSTGRES_OBJ_STORAGE_URL_SYNC
    versions_path = get_version_path(db)

    config.set('alembic', 'version_locations', str(versions_path))
    config.set('alembic', 'sqlalchemy.url', str(db_url))
    config.set('alembic', 'script_location', str(ALEMBIC_PATH))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_config_file:
        config.write(temp_config_file)
        temp_config_file_path = temp_config_file.name
    updated_config = Config(temp_config_file_path)
    try:
        yield updated_config
    finally:
        temp_config_file.close()


def get_next_version_index(versions_path: Path) -> int:
    return sum(1 for _ in versions_path.iterdir() if _.is_file())


def get_current_version_index(db: DBEnum, versions_path: Path):
    current_version_str = get_current_version(db)
    versions_files = os.listdir(versions_path)
    for filename in versions_files:
        if filename.startswith(f'{current_version_str}_'):
            index = int(filename.split('_')[1])
            return index


def get_version_path(db: DBEnum) -> Path:
    return BASE_DIR / f'alembic/versions_{db}'


def get_args() -> tuple[DBEnum, str] | None:
    "get 'db' and 'message' args"
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', type=str, help='Message string')
    parser.add_argument('-db', '--database', type=str, help='Database to manipulate')

    args = parser.parse_args()
    message = args.message

    db = args.database
    valid_dbs = [x.value for x in DBEnum]
    assert db in valid_dbs, f"you must provide valid database ({valid_dbs=:}), use '-db database_str'"
    return db, message
