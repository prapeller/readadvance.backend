import datetime as dt
from enum import Enum

import pydantic as pd

from core.enums import LanguagesISO2NamesEnum, LevelCEFRCodesEnum


class WordUpdateSerializer(pd.BaseModel):
    characters: str | None = None
    lemma: str | None = None
    pos: str | None = None
    language_iso_2: LanguagesISO2NamesEnum | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None


class WordCreateSerializer(WordUpdateSerializer):
    characters: str
    lemma: str | None = None
    pos: str | None = None
    language_iso_2: LanguagesISO2NamesEnum | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None


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
    language_iso_2: LanguagesISO2NamesEnum | None = None
    level_cefr_code: LevelCEFRCodesEnum | None = None


async def word_params_dependency(
        language_iso_2: LanguagesISO2NamesEnum,
        characters: str | None = None,
        lemma: str | None = None,
        pos: str | None = None,
        created_at: dt.datetime | None = None,
        updated_at: dt.datetime | None = None,
        level_cefr_code: LevelCEFRCodesEnum | None = None,
):
    return {
        'language_iso_2': language_iso_2,
        'characters': characters,
        'lemma': lemma,
        'pos': pos,
        'created_at': created_at,
        'updated_at': updated_at,
        'level_cefr_code': level_cefr_code,
    }


class WordsPaginatedSerializer(pd.BaseModel):
    words: list[WordReadSerializer] = []
    total_count: int
    filtered_count: int
