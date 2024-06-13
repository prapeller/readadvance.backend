import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from db import BaseObjStorage, Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


# Base is for 'postgres_readstash' db
# BaseObjStorage is for 'postgre_obj_storage' db

class FileIndexModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'file_index'

    name = sa.Column(sa.String)
    content_type = sa.Column(sa.String)
    file_storage_uuid = sa.Column(sa.UUID(as_uuid=False), unique=True, nullable=False)

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.file_storage_uuid=}, {self.name=}, {self.content_type=}')


class FileStorageModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, BaseObjStorage):
    __tablename__ = 'file_storage'

    file_data = sa.Column(postgresql.BYTEA(), nullable=False)

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}')
