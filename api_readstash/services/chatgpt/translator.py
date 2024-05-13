import asyncio

from core.constants import LANGUAGES_DICT
from core.enums import ChatGPTModelsEnum, LanguagesISO2NamesEnum, TranslationMethodsEnum
from services.chatgpt.chatgpt import ChatGPT


async def get_translation_chatgpt(model: ChatGPTModelsEnum,
                                  lang_iso2: LanguagesISO2NamesEnum,
                                  target_language: str,
                                  input: str) -> tuple[LanguagesISO2NamesEnum, str, ChatGPTModelsEnum]:
    """Sends a message to OpenAI's GPT-4 model and returns the response."""

    chatgpt = ChatGPT(model=model,
                      prompt=f"you are translator."
                             f"your reply must consist only of needed translation without any additional information"
                             f"in the output try to make the same punctuation, capitalization etc like in input.")

    resp_text = await chatgpt.get_response_text(f"provide translation of '{input}' to {target_language}")
    try:
        return lang_iso2, resp_text, model
    except KeyError:
        # Handle cases where the response may not contain the expected data
        return lang_iso2, "Translation error or no response.", model


async def get_translations_chatgpt(model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
                                   lang_iso2_base: LanguagesISO2NamesEnum = LanguagesISO2NamesEnum.EN,
                                   input_base: str | None = None,
                                   method_base: TranslationMethodsEnum = TranslationMethodsEnum.manual,
                                   ):
    """Translates text to the specified language using OpenAI's GPT-4 model."""
    assert input_base is not None, "input_base must be provided"
    translations = {}
    translation_tasks = []
    for lang_iso2 in LanguagesISO2NamesEnum:
        if lang_iso2 == lang_iso2_base:
            translations[lang_iso2] = (input_base, method_base)
        else:
            target_lang = LANGUAGES_DICT.get(lang_iso2)[2]
            task = get_translation_chatgpt(model, lang_iso2, target_lang, input_base)
            translation_tasks.append(task)
    translations_results = await asyncio.gather(*translation_tasks)
    for lang_iso2, translation, model in translations_results:
        translations[lang_iso2] = translation, model
    return translations
