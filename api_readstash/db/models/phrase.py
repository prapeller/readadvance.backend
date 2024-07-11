import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import CreatedUpdatedMixin, IdentifiedWithIntMixin, IdentifiedWithUuidMixin


class PhraseModel(IdentifiedWithIntMixin, IdentifiedWithUuidMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'phrase'

    content = sa.Column(sa.Text, nullable=False)

    user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid', ondelete='CASCADE'),
                          nullable=False)  # creator uuid

    user_creator = relationship('UserModel', back_populates='created_phrases',
                                primaryjoin='PhraseModel.user_uuid==UserModel.uuid')

    def __repr__(self):
        return (f'{self.__class__.__name__} '
                f'{self.id=}, {self.uuid=}')
