import sqlalchemy as sa

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class TextModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'readstash_text'

    content = sa.Column(sa.Text, nullable=False)
    level_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('level.uuid', ondelete='SET NULL'),
                              nullable=True)
    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'),
                           nullable=False)