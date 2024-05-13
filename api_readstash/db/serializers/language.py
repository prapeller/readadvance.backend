import datetime as dt

import pydantic as pd

from core.enums import LanguagesISO2NamesEnum


class LanguageUpdateSerializer(pd.BaseModel):
    name: str | None = None
    iso2: LanguagesISO2NamesEnum | None = None


class LanguageCreateSerializer(LanguageUpdateSerializer):
    name: str
    iso2: LanguagesISO2NamesEnum


class LanguageReadSerializer(LanguageCreateSerializer):
    id: int
    uuid: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        from_attributes = True


LanguageReadSerializer.model_rebuild()
