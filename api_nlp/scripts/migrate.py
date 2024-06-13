from pathlib import Path

from alembic import command

from core.alembic_helpers import (
    get_updated_alembic_config,
    get_args,
    get_current_version_index,
    get_version_path,
)
from core.enums import DBEnum
from core.logger_config import setup_logger

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


def migrate(db: DBEnum, current_version_index=None, to_migrate_version_index=None):
    updated_config = get_updated_alembic_config(db)
    if current_version_index is None and to_migrate_version_index is None:
        command.upgrade(next(updated_config), "head")
    else:
        diff = to_migrate_version_index - current_version_index
        if diff > 0:
            command.upgrade(next(updated_config), f'+{diff}')
        else:
            command.downgrade(next(updated_config), f'{diff}')


if __name__ == '__main__':
    db, message = get_args()
    print(f'{db=:}, {message=:}')
    versions_path = get_version_path(db)
    to_migrate_version_index = None

    if message is not None:
        try:
            to_migrate_version_index = int(message)
        except ValueError:
            raise ValueError("this is not 'init' migration, you must provide index number, use '-m version_index_int'")
        current_version_index = get_current_version_index(db, versions_path)
        migrate(db, current_version_index, to_migrate_version_index)
    else:
        migrate(db)
