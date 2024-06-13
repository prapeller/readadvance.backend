from core.enums import ChatGPTModelsEnum, LanguagesISO2NamesEnum, LevelSystemNamesEnum, LevelCEFRCodesEnum
from core.exceptions import ChatgptException, TextIdentifierException
from services.chatgpt.chatgpt import ChatGPT


async def get_text_language_chatgpt(
        text: str,
        model: ChatGPTModelsEnum) -> LanguagesISO2NamesEnum:

    chatgpt = ChatGPT(model=model,
                      prompt=f"you are text language identifier. "
                             f"your reply must consist only of needed language iso2 code. "
                             f"without any additional information.")
    truncated_text = text[:1000]
    try:
        language_code = await chatgpt.get_response_text(
            f"provide language code of '{truncated_text}'. valid codes: {[l for l in LanguagesISO2NamesEnum]}")
        assert language_code in (c for c in
                                 LanguagesISO2NamesEnum), f'Invalid language code was identified: {language_code}'
    except (AssertionError, ChatgptException) as e:
        raise TextIdentifierException(f'During text language identification error: {e}')
    return language_code


async def get_text_level_chatgpt(
        text: str,
        model: ChatGPTModelsEnum,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR) -> LevelCEFRCodesEnum:

    chatgpt = ChatGPT(model=model,
                      prompt=f"you are text level identifier. "
                             f"your reply must consist only of needed level of {system} code. "
                             f"without any additional information.")
    truncated_text = text[:1000]
    try:
        level = await chatgpt.get_response_text(
            f"provide level of '{truncated_text}'. in {system=}, valid levels: {[l for l in LevelCEFRCodesEnum]}")
        assert level in (l for l in LevelCEFRCodesEnum), f'Invalid level was identified: {level}'
    except (AssertionError, ChatgptException) as e:
        raise TextIdentifierException(f'During text level identification error: {e}')
    return level
