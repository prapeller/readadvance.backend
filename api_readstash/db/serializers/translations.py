import pydantic as pd

from core.enums import LanguagesISO2NamesEnum
from db.serializers.word import WordReadSerializer


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
    word_input: str
    word_output: str
    word_pos: str
    context_output: str
    input_lang_iso2: LanguagesISO2NamesEnum
    target_lang_iso2: LanguagesISO2NamesEnum
    lemma_word: 'WordReadSerializer'
    word_image_file_index_uuid: pd.UUID4 | None = None
