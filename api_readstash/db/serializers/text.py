import datetime as dt
from enum import Enum

import pydantic as pd

from core.enums import LevelCEFRCodesEnum, LanguagesISO2NamesEnum


class TextUpdateSerializer(pd.BaseModel):
    user_uuid: str | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None
    language_iso_2: LanguagesISO2NamesEnum | None = None


class TextCreateSerializer(TextUpdateSerializer):
    content: str

    user_uuid: str | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None
    language_iso_2: LanguagesISO2NamesEnum | None = None


class TextReadNoContentSerializer(pd.BaseModel):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    user_uuid: str | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None
    language_iso_2: LanguagesISO2NamesEnum | None = None

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
    level_cefr_code = 'level_cefr_code'
    language_iso_2 = 'language_iso_2'


async def text_params_dependency(
        created_at: dt.datetime | None = None,
        updated_at: dt.datetime | None = None,
        level_cefr_code: LevelCEFRCodesEnum | None = None,
        language_iso_2: LanguagesISO2NamesEnum | None = None,
):
    return {
        'created_at': created_at,
        'updated_at': updated_at,
        'level_cefr_code': level_cefr_code,
        'language_iso_2': language_iso_2,
    }


class TextsPaginatedSerializer(pd.BaseModel):
    texts: list[TextReadContentSerializer] = []
    total_count: int
    filtered_count: int
