import datetime as dt

import pydantic as pd

from core.enums import LevelOrderEnum, LevelCEFRCodesEnum


class LevelUpdateSerializer(pd.BaseModel):
    order: LevelOrderEnum | None = None
    cefr_code: LevelCEFRCodesEnum | None = None


class LevelCreateSerializer(LevelUpdateSerializer):
    order: LevelOrderEnum
    cefr_code: LevelCEFRCodesEnum


class LevelReadSerializer(LevelCreateSerializer):
    id: int
    uuid: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
