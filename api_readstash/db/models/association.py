import sqlalchemy as sa

from db import Base
from db.models._shared import IdentifiedWithIntMixin


class WordFileUserStatusAssoc(IdentifiedWithIntMixin, Base):
    __tablename__ = 'word_file_user_status'

    word_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('word.uuid', ondelete='CASCADE'), nullable=False)
    file_index_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('file_index.uuid', ondelete='CASCADE'), nullable=True)
    user_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'), nullable=True)
    status = sa.Column(sa.String(10), index=True)

    # file_index = relationship('FileIndexModel', backref='word_file_user_statuses')

    __table_args__ = (
        # unique word created by admin (user_uuid is NULL, status is NULL)
        # unique word created by user (user_uuid is uuid, status is varchar)
        sa.UniqueConstraint(
            'user_uuid', 'word_uuid', 'file_index_uuid', 'status', name='unique_user_uuid_word_uuid_file_index_uuid'),
    )
