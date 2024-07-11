import pydantic as pd

from core.enums import LanguagesISO2NamesEnum


class TranslNlpAPIInSerializer(pd.BaseModel):
    text_input: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum


class TranslNlpAPIOutSerializer(pd.BaseModel):
    text_output: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum



class TranslWordInSerializer(pd.BaseModel):
    word_input: str
    context_input: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum


class TranslWordOutSerializer(pd.BaseModel):
    word_output: str
    word_pos: str
    context_output: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum