import pydantic as pd

from core.enums import LanguagesISO2NamesEnum


class AnalysesInSerializer(pd.BaseModel):
    content: str | None = None
    iso2: LanguagesISO2NamesEnum | None = None


class AnalysesOutSerializer(pd.BaseModel):
    words: list[dict] | None = None
    iso2: LanguagesISO2NamesEnum | None = None
