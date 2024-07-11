import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin, IsActiveMixin


class GrammarModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, IsActiveMixin, Base):
    __tablename__ = 'grammar'

    name = sa.Column(JSONB, nullable=False, server_default=sa.text('\'{}\'::json'))
    explanation = sa.Column(JSONB, nullable=False, server_default=sa.text('\'{}\'::json'))
    examples = sa.Column(JSONB, nullable=False, server_default=sa.text('\'[]\'::json'))
    language_iso_2 = sa.Column(sa.String(2), nullable=True, index=True)
    level_cefr_code = sa.Column(sa.String(2), nullable=True, index=True)

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.name=}')
