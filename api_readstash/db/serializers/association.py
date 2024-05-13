import pydantic as pd

from core.enums import UserWordStatusEnum


class WordFileUserStatusUpdateSerializer(pd.BaseModel):
    word_uuid: str | None = None
    user_uuid: str | None = None
    file_index_uuid: str | None = None
    status: UserWordStatusEnum | None = None


class WordFileUserStatusCreateSerializer(WordFileUserStatusUpdateSerializer):
    word_uuid: str
    user_uuid: str | None = None
    file_index_uuid: str | None = None
    status: UserWordStatusEnum | None = None


class WordFileUserStatusReadSerializer(WordFileUserStatusCreateSerializer):
    id: int
