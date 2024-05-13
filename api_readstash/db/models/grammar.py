import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class GrammarModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'grammar'

    name = sa.Column(JSONB, nullable=False, server_default=sa.text('\'{}\'::json'))
    explanation = sa.Column(JSONB, nullable=False, server_default=sa.text('\'{}\'::json'))
    examples = sa.Column(JSONB, nullable=False, server_default=sa.text('\'[]\'::json'))

    language_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('language.uuid', ondelete='SET NULL'), nullable=False, index=True)
    level_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('level.uuid', ondelete='SET NULL'), nullable=False, index=True)
