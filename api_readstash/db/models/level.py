import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class LevelModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'level'

    order = sa.Column(sa.Integer, nullable=False)
    cefr_code = sa.Column(sa.String(2), nullable=False)

    words = relationship('WordModel', back_populates='level', lazy='joined')
    texts = relationship('TextModel', back_populates='level', lazy='joined')

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.cefr_code=}, {self.order=}')
