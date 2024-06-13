import pydantic as pd

from core.enums import LanguagesISO2NamesEnum


class TextSerializer(pd.BaseModel):
    content: str | None = None
    iso2: LanguagesISO2NamesEnum | None = None


class TextReadWordsSerializer(pd.BaseModel):
    words: list[str] | None = None
    iso2: LanguagesISO2NamesEnum | None = None
