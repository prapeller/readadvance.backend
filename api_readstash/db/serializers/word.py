import datetime as dt
from enum import Enum

import pydantic as pd


class WordUpdateSerializer(pd.BaseModel):
    characters: str | None = None
    language_uuid: str | None = None
    level_uuid: str | None = None


class WordCreateSerializer(WordUpdateSerializer):
    characters: str
    language_uuid: str
    level_uuid: str | None = None


class WordReadSerializer(WordCreateSerializer):
    id: int
    uuid: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        from_attributes = True


class WordOrderByEnum(str, Enum):
    created_at = 'created_at'
    updated_at = 'updated_at'
    characters = 'characters'
    language_uuid = 'language_uuid'
    level_uuid = 'level_uuid'


async def word_params_dependency(
        language_uuid: str,
        characters: str | None = None,
        created_at: dt.datetime | None = None,
        updated_at: dt.datetime | None = None,
        level_uuid: str | None = None,
):
    return {
        'language_uuid': language_uuid,
        'characters': characters,
        'created_at': created_at,
        'updated_at': updated_at,
        'level_uuid': level_uuid,
    }


class WordsPaginatedSerializer(pd.BaseModel):
    words: list[WordReadSerializer] = []
    total_count: int
    filtered_count: int
