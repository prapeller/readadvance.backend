import datetime as dt

import pydantic as pd

from core.enums import LevelOrderEnum, LevelCEFRCodesEnum


class LevelUpdateSerializer(pd.BaseModel):
    language_uuid: str | None = None
    order: LevelOrderEnum | None = None
    cefr_code: LevelCEFRCodesEnum | None = None
    native_code: LevelCEFRCodesEnum | None = None


class LevelCreateSerializer(LevelUpdateSerializer):
    language_uuid: str
    order: LevelOrderEnum
    cefr_code: LevelCEFRCodesEnum
    native_code: LevelCEFRCodesEnum | None = None


class LevelReadSerializer(LevelCreateSerializer):
    id: int
    uuid: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
