import datetime as dt
from enum import Enum

import pydantic as pd


class TextUpdateSerializer(pd.BaseModel):
    user_uuid: str | None = None
    level_uuid: str | None = None
    language_uuid: str | None = None


class TextCreateSerializer(TextUpdateSerializer):
    content: str

    user_uuid: str | None = None
    level_uuid: str | None = None
    language_uuid: str | None = None


class TextReadNoContentSerializer(pd.BaseModel):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    user_uuid: str | None = None
    level_uuid: str | None = None
    language_uuid: str | None = None

    class Config:
        from_attributes = True


class TextReadContentSerializer(TextReadNoContentSerializer):
    content: str

    class Config:
        from_attributes = True


class TextOrderByEnum(str, Enum):
    created_at = 'created_at'
    updated_at = 'updated_at'
    characters = 'characters'
    level_uuid = 'level_uuid'
    language_uuid = 'language_uuid'


async def text_params_dependency(
        created_at: dt.datetime | None = None,
        updated_at: dt.datetime | None = None,
        level_uuid: str | None = None,
        language_uuid: str | None = None,
):
    return {
        'created_at': created_at,
        'updated_at': updated_at,
        'language_uuid': language_uuid,
        'level_uuid': level_uuid,
    }


class TextsPaginatedSerializer(pd.BaseModel):
    texts: list[TextReadContentSerializer] = []
    total_count: int
    filtered_count: int
