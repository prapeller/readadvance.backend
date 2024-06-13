import pydantic as pd

from core.enums import UserWordStatusEnum, UserTextStatusEnum


class UserWordStatusFileUpdateSerializer(pd.BaseModel):
    word_uuid: str | None = None
    user_uuid: str | None = None
    file_index_uuid: str | None = None
    status: UserWordStatusEnum | None = None


class UserWordStatusFileCreateSerializer(UserWordStatusFileUpdateSerializer):
    word_uuid: str
    user_uuid: str | None = None
    file_index_uuid: str | None = None
    status: UserWordStatusEnum | None = None


class UserWordStatusFileReadSerializer(UserWordStatusFileCreateSerializer):
    id: int


class UserTextStatusUpdateSerializer(pd.BaseModel):
    text_uuid: str | None = None
    user_uuid: str | None = None
    status: UserTextStatusEnum | None = None


class UserTextStatusCreateSerializer(UserTextStatusUpdateSerializer):
    text_uuid: str
    user_uuid: str | None = None
    status: UserTextStatusEnum | None = None


class UserTextStatusReadSerializer(UserTextStatusCreateSerializer):
    id: int
