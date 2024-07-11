import pydantic as pd

from core.enums import LanguagesISO2NamesEnum


class TranslInSerializer(pd.BaseModel):
    text_input: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum


class TranslOutSerializer(pd.BaseModel):
    text_output: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum