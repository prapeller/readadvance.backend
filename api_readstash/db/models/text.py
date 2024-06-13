import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class TextModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'text'

    content = sa.Column(sa.Text, nullable=False)

    level_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('level.uuid', ondelete='SET NULL'),
                           nullable=True)
    language_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('language.uuid', ondelete='SET NULL'),
                              nullable=True)
    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'),
                          nullable=False)  # creator uuid

    user_creator = relationship('UserModel', back_populates='created_texts',
                                primaryjoin='TextModel.user_uuid==UserModel.uuid')
    language = relationship('LanguageModel', back_populates='texts',
                            primaryjoin='TextModel.language_uuid==LanguageModel.uuid')
    level = relationship('LevelModel', back_populates='texts',
                         primaryjoin='TextModel.level_uuid==LevelModel.uuid')

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.language_uuid=}')
