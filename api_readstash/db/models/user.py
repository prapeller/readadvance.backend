import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class UserModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'user'

    email = sa.Column(sa.String(50), unique=True, index=True)
    first_name = sa.Column(sa.String(50), index=True)
    last_name = sa.Column(sa.String(50), index=True)
    timezone = sa.Column(sa.String(10), nullable=False, server_default=sa.text("'UTC+3'::character varying"))

    telegram_id = sa.Column(sa.String(255))
    is_accepting_emails = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))
    is_accepting_interface_messages = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))
    is_accepting_telegram = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('false'))
    roles = sa.Column(JSONB, nullable=False, server_default=sa.text('\'[]\'::json'))

    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))

    def __eq__(self, other):
        return isinstance(other, UserModel) and self.id == other.id and self.email == other.email

    def __repr__(self):
        return f'<UserModel> ({self.id=:}, {self.uuid=:}, {self.email=:})'
