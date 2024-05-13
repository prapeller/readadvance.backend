import sqlalchemy as sa
from sqlalchemy.orm import relationship
from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class LanguageModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'language'

    name = sa.Column(sa.String(50), nullable=False)
    iso2 = sa.Column(sa.String(2), nullable=False)

    words = relationship('WordModel', back_populates='language')
