import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin, IsActiveMixin
from db.models.file_storage import FileIndexModel


class WordModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, IsActiveMixin, Base):
    """
    table for words.
    words are being created by admin or app.
    when user upload text - app checks its language, and for every word searches it in db
        if it is created in this lang - pass
        if not - creates 'inactive' word so 'lang admin' later could make it 'active' and create translations for other langs
    users can add word them to their word list to set status and create own files.
    """
    __tablename__ = 'word'

    characters = sa.Column(sa.String(50), nullable=False)

    language_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('language.uuid', ondelete='SET NULL'),
                              nullable=False, index=True)
    level_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('level.uuid', ondelete='SET NULL'), index=True)

    language = relationship('LanguageModel', back_populates='words',
                            primaryjoin='WordModel.language_uuid==LanguageModel.uuid')
    level = relationship('LevelModel', back_populates='words',
                         primaryjoin='WordModel.level_uuid==LevelModel.uuid')

    translations = relationship(
        'WordModel',
        secondary='word_translation',
        primaryjoin='WordTranslationAssoc.word_uuid_original == WordModel.uuid',
        secondaryjoin='WordTranslationAssoc.word_uuid_translated == WordModel.uuid',
    )

    translations_to_language = relationship(
        "WordModel",
        secondary="word_translation",
        primaryjoin="WordTranslationAssoc.word_uuid_original == WordModel.uuid",
        secondaryjoin="and_(WordTranslationAssoc.word_uuid_translated == WordModel.uuid, "
                      "WordModel.language_uuid == bindparam('language_uuid'))",
        viewonly=True,
    )

    _image_file_index = relationship('FileIndexModel',
                                     secondary='user_word_status_file',
                                     primaryjoin="and_(WordModel.uuid == UserWordStatusFileAssoc.word_uuid, "
                                                 "UserWordStatusFileAssoc.user_uuid == None, "
                                                 "UserWordStatusFileAssoc.file_index_uuid == FileIndexModel.uuid, "
                                                 "FileIndexModel.content_type.like('image'))",
                                     viewonly=True)

    _audio_file_index = relationship('FileIndexModel',
                                     secondary='user_word_status_file',
                                     primaryjoin="and_(WordModel.uuid == UserWordStatusFileAssoc.word_uuid, "
                                                 "UserWordStatusFileAssoc.user_uuid == None, "
                                                 "UserWordStatusFileAssoc.file_index_uuid==FileIndexModel.uuid, "
                                                 "FileIndexModel.content_type.like('audio'))",
                                     viewonly=True)

    _users_image_file_indexes = relationship('FileIndexModel',
                                             secondary='user_word_status_file',
                                             primaryjoin="and_(WordModel.uuid == UserWordStatusFileAssoc.word_uuid, "
                                                         "UserWordStatusFileAssoc.file_index_uuid==FileIndexModel.uuid, "
                                                         "FileIndexModel.content_type.like('image'))",
                                             uselist=True,
                                             viewonly=True)

    # IMAGE_FILE_INDEX
    @hybrid_property
    def image_file_index(self):
        return self._image_file_index

    @image_file_index.setter
    def image_file_index(self, file_index: FileIndexModel):
        self._image_file_index = file_index

    @image_file_index.expression
    def image_file_index(cls):
        return cls._image_file_index

    # AUDIO_FILE_INDEX
    @hybrid_property
    def audio_file_index(self):
        return self._audio_file_index

    @audio_file_index.setter
    def audio_file_index(self, file_index: FileIndexModel):
        self._audio_file_index = file_index

    @audio_file_index.expression
    def audio_file_index(cls):
        return cls._audio_file_index

    # USERS_IMAGE_FILE_INDEXES
    @hybrid_property
    def users_image_file_indexes(self):
        return self._users_image_file_indexes

    @users_image_file_indexes.expression
    def users_image_file_indexes(cls):
        return cls._users_image_file_indexes

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.language_uuid=}, {self.characters=}')
