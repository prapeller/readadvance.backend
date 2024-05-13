import asyncio

from core.constants import LEVEL_SYSTEM_ORDERS_CODES
from core.enums import ChatGPTModelsEnum, LanguagesISO2NamesEnum, LevelSystemNamesEnum, LevelCEFRCodesEnum
from db.models.word import WordModel
from services.chatgpt.chatgpt import ChatGPT


async def get_word_level_chatgpt(
        word: str,
        lang_iso2: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR) -> tuple[str, LevelCEFRCodesEnum, ChatGPTModelsEnum]:
    """Sends a message to OpenAI's GPT-4 model and returns the response."""

    chatgpt = ChatGPT(model=model,
                      prompt=f"you are word level identifier."
                             f"your reply must consist only of needed level of requested system, "
                             f"without any additional information.")

    level = await chatgpt.get_response_text(
        f"provide level of '{word}' (in {lang_iso2}). in {system=}, valid levels: {(val for key, val in LEVEL_SYSTEM_ORDERS_CODES[system])}")
    try:
        return word, level, model
    except KeyError:
        # Handle cases where the response may not contain the expected data
        return word, LevelCEFRCodesEnum.NOT_IDENTIFIED, model


async def get_words_levels_chatgpt(
        words: list[WordModel],
        model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR
) -> dict[str, tuple[LevelCEFRCodesEnum, ChatGPTModelsEnum]]:
    """Identifies the level of words using OpenAI's GPT-4 model."""

    word_levels = {}
    tasks = []
    for word in words:
        task = get_word_level_chatgpt(word.characters, word.language.iso2, model, system)
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    for word, level, model in results:
        word_levels[word] = level, model
    return word_levels
