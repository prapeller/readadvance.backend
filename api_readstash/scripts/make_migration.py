from pathlib import Path

from alembic import command

from core.alembic_helpers import (
    get_updated_alembic_config,
    get_next_version_index,
    get_args, get_version_path,
)
from core.config import BASE_DIR
from core.enums import DBEnum
from core.logger_config import setup_logger

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


ALEMBIC_PATH = BASE_DIR / 'alembic'


def make_migration(db: DBEnum, message: str, version_index: int):
    migration_message = f'{version_index}_{message}'
    updated_config = get_updated_alembic_config(db)
    command.revision(next(updated_config), autogenerate=True, message=migration_message)


if __name__ == '__main__':
    db, message = get_args()
    versions_path = get_version_path(db)
    next_version_index = get_next_version_index(versions_path)

    if message is None and next_version_index == 0:
        message = 'init'
    if message is None and next_version_index != 0:
        raise ValueError("this is not 'init' migration, you must provide message, use '-m message'")

    make_migration(db, message, next_version_index)
