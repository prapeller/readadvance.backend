import sqlalchemy as sa

from sqlalchemy.orm import relationship
from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class LevelModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'level'

    language_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('language.uuid', ondelete='SET NULL'),
                              nullable=False, index=True)
    order = sa.Column(sa.Integer, nullable=False)
    cefr_code = sa.Column(sa.String(2), nullable=False)
    native_code = sa.Column(sa.String(10))

    words = relationship('WordModel', back_populates='level', lazy='joined')