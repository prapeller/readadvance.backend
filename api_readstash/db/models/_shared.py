import sqlalchemy as sa


class IdentifiedWithIntMixin:
    id = sa.Column(sa.Integer, primary_key=True)


class IdentifiedWithUuidMixin:
    uuid = sa.Column(sa.UUID(as_uuid=False), server_default=sa.text("uuid_generate_v4()"), unique=True, nullable=False)

class IsActiveMixin:
    is_active = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))

class CreatedUpdatedMixin:
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.current_timestamp(), nullable=True)
