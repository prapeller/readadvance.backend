import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class TextModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'text'

    content = sa.Column(sa.Text, nullable=False)
    language_iso_2 = sa.Column(sa.String(2), nullable=True)
    level_cefr_code = sa.Column(sa.String(2), nullable=True)

    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'),
                          nullable=False)  # creator uuid

    user_creator = relationship('UserModel', back_populates='created_texts',
                                primaryjoin='TextModel.user_uuid==UserModel.uuid')

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}, {self.language_iso_2=}')
