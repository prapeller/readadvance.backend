from core.enums import ChatGPTModelsEnum, LanguagesISO2NamesEnum, LevelSystemNamesEnum, LevelCEFRCodesEnum
from core.exceptions import ChatgptException, WordIdentifierException
from services.chatgpt.chatgpt import ChatGPT


async def get_word_level_chatgpt(
        word: str,
        lang_iso2: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR) -> LevelCEFRCodesEnum:

    chatgpt = ChatGPT(model=model,
                      prompt=f"you are word level identifier. "
                             f"your reply must consist only of needed level of {system} code. "
                             f"without any additional information.")
    try:
        level = await chatgpt.get_response_text(
            f"provide level of '{word}' (in {lang_iso2}). in {system=}, valid levels: {[l for l in LevelCEFRCodesEnum]}")
        assert level in (l for l in LevelCEFRCodesEnum), f'Invalid level code was identified: {level}'
    except (AssertionError, ChatgptException) as e:
        raise WordIdentifierException(f'During word level identification error: {e}')
    return level
