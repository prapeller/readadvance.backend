import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin, IsActiveMixin


class LanguageModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, IsActiveMixin, Base):
    __tablename__ = 'language'

    name = sa.Column(sa.String(50), nullable=False)
    iso2 = sa.Column(sa.String(2), nullable=False)

    words = relationship('WordModel', back_populates='language')
    texts = relationship('TextModel', back_populates='language')
    phrases = relationship('PhraseModel', back_populates='language')

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.name=}, {self.iso2=}')
