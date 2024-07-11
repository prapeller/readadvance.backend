from core.enums import ChatGPTModelsEnum, LanguagesISO2NamesEnum, LevelSystemNamesEnum, LevelCEFRCodesEnum
from core.exceptions import ChatgptException, TextIdentifierException
from services.chatgpt.chatgpt import ChatGPT


async def identify_text_language_chatgpt(
        text: str,
        model: ChatGPTModelsEnum) -> LanguagesISO2NamesEnum:
    chatgpt = ChatGPT(model=model,
                      prompt=f"You are text language identifier. "
                             f"Your reply must consist only of needed language iso2 code.")
    truncated_text = text[:1000]
    try:
        language_code = await chatgpt.get_response_text(
            f"provide language code of '{truncated_text}'. valid codes: {[l for l in LanguagesISO2NamesEnum]}")
        assert language_code in (c for c in
                                 LanguagesISO2NamesEnum), f'Invalid language code was identified: {language_code}'
    except (AssertionError, ChatgptException) as e:
        raise TextIdentifierException(f'During text language identification error: {e}')
    return language_code


async def identify_text_level_chatgpt(
        text: str,
        model: ChatGPTModelsEnum,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR) -> LevelCEFRCodesEnum:
    chatgpt = ChatGPT(model=model,
                      prompt=f"You are text level identifier. "
                             f"Your reply must consist only of one of valid levels.")
    truncated_text = text[:1000]
    try:
        level = await chatgpt.get_response_text(
            f"'{truncated_text=}', {system=}, valid_levels={[l for l in LevelCEFRCodesEnum]}")
        assert level in (l for l in LevelCEFRCodesEnum), f'Invalid level was identified: {level}'
    except (AssertionError, ChatgptException) as e:
        raise TextIdentifierException(f'During text level identification error: {e}')
    return level
