import sqlalchemy as sa

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin, IsActiveMixin


class UserWordStatusFileAssoc(IdentifiedWithIntMixin, Base):
    """association table for user's words, their status and files."""
    __tablename__ = 'user_word_status_file'

    user_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'), nullable=True)
    word_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('word.uuid', ondelete='CASCADE'), nullable=False, index=True)
    status = sa.Column(sa.String(10), index=True)
    file_index_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('file_index.uuid', ondelete='CASCADE'), nullable=True, index=True)

    __table_args__ = (
        # unique for word: file (created by admin), status (set to NULL)     (user_uuid is NULL, status is NULL)
        # unique for word: file (created by user),  status (created by user) (user_uuid is uuid, status is varchar)
        sa.UniqueConstraint(
            'user_uuid', 'word_uuid', 'status', 'file_index_uuid',
            name='unique_user_uuid_word_uuid_status_file_index_uuid'),
    )

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.user_uuid=}, {self.word_uuid=}, {self.status=}, {self.file_index_uuid=}')


class UserTextStatusAssoc(IdentifiedWithIntMixin, Base):
    """association table for user's texts, their status."""
    __tablename__ = 'user_text_status'

    user_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'), nullable=True)
    text_uuid = sa.Column(
        sa.UUID(as_uuid=False), sa.ForeignKey('text.uuid', ondelete='CASCADE'), nullable=False, index=True)
    status = sa.Column(sa.String(10), index=True)

    __table_args__ = (
        # unique for text (created by admin/ai) status (set to (created by user) to text
        # unique status (created by user) to text
        sa.UniqueConstraint(
            'user_uuid', 'text_uuid', 'status',
            name='unique_user_uuid_text_uuid_status'),
    )

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.user_uuid=}, {self.text_uuid=}, {self.status=}')


# class WordTranslationAssoc(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, IsActiveMixin, Base):
#     __tablename__ = 'word_translation'
#
#     word_uuid_original = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('word.uuid', ondelete='CASCADE'),
#                                    nullable=False, index=True)
#     word_uuid_translated = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('word.uuid', ondelete='CASCADE'),
#                                      nullable=False, index=True)
#     popularity_count = sa.Column(sa.Integer, nullable=False)
#
#     word_original = relationship('WordModel',
#                                  primaryjoin='WordTranslationModel.word_uuid_original == WordModel.uuid',
#                                  back_populates='translations')
#     word_translated = relationship('WordModel',
#                                    primaryjoin='WordTranslationModel.word_uuid_translated == WordModel.uuid')
#
#     def __repr__(self):
#         return (f'{self.__class__.__name__} '
#                 f'{self.id=}, {self.uuid=}')
