import json

from core.constants import PARTS_OF_SPEECH
from core.enums import LanguagesISO2NamesEnum, ChatGPTModelsEnum, LevelSystemNamesEnum, LevelCEFRCodesEnum
from services.chatgpt.chatgpt import ChatGPT


async def identify_word_level_chatgpt(
        word_input: str,
        input_lang_iso2: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        system: LevelSystemNamesEnum = LevelSystemNamesEnum.CEFR,
) -> LevelCEFRCodesEnum:
    response_word_par_ex_1 = """
        {
          "level_cefr_code": "..." 
        }
        """
    valid_codes = [l for l in LevelCEFRCodesEnum]
    prompt = f"""You are word's CEFR level identifier.
        Your response must be exactly as the following example:
        {response_word_par_ex_1}
        valid codes: {valid_codes}
        """

    chatgpt = ChatGPT(model=model, prompt=prompt)
    resp_text = await chatgpt.get_response_text(f"'{word_input=}', '{input_lang_iso2=}'")
    resp_dict = json.loads(resp_text)
    level_cefr_code = resp_dict['level_cefr_code']
    assert level_cefr_code in valid_codes, 'not valid code was identified'
    return level_cefr_code


async def identify_word_part_of_speech_chatgpt(
        text_input: str,
        input_lang_iso2: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
) -> dict:
    response_word_par_ex_1 = """
    {
      "word_pos": "..." 
    }
    """

    prompt = f"""You are speech part identifier.
    Your response must be exactly as the following example:
    {response_word_par_ex_1}
    Valid pos vars: {', '.join(PARTS_OF_SPEECH[input_lang_iso2].values())}
    """

    chatgpt = ChatGPT(model=model, prompt=prompt)
    resp_text = await chatgpt.get_response_text(f"'{text_input=}', '{input_lang_iso2=}'")
    return json.loads(resp_text)


async def identify_word_lemma_chatgpt(
        input_text: str,
        input_language_iso2_name: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
) -> dict:
    """Translates single word in some context to the specified language using OpenAI's GPT-4 model"""
    response_word_lemma_ex_1 = """
    {
      "lemma": "..."
    }
    """

    prompt = f"""You are lemmatizator. 
    Your response must be exactly as the following example:
    {response_word_lemma_ex_1}
    Punctuation, capitalization must be the same as in provided input.
    """

    chatgpt = ChatGPT(model=model, prompt=prompt)
    resp_text = await chatgpt.get_response_text(f"'{input_text=}', '{input_language_iso2_name=}'")
    return json.loads(resp_text)
