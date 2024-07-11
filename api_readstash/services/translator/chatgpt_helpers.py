import json

from core.constants import PARTS_OF_SPEECH
from core.enums import LanguagesISO2NamesEnum, ChatGPTModelsEnum
from db.serializers.translations import TranslWordOutSerializer
from services.chatgpt.chatgpt import ChatGPT


async def translate_word_chatgpt(
        word_input: str,
        input_lang_iso2: LanguagesISO2NamesEnum,
        target_lang_iso2: LanguagesISO2NamesEnum,
        context_input: str | None = None,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
) -> TranslWordOutSerializer:
    """Translates single word in some context to the specified language using OpenAI's GPT model"""

    response_example = """
    {
      "word_output": "...",
      "word_pos": "...",
      "context_output": "..."
    }
    """
    prompt = f"""You are word translator.
    I provide you input vars.
    word_input is taken from context_input. 
    context_output must be translation of context_input.  
    word_output must be the same way connected context_output but as lemma.
    Punctuation, capitalization must be the same as in provided input.
    Valid pos vars: {', '.join(PARTS_OF_SPEECH[target_lang_iso2].values())}
    Your response must be exactly as the following example:
    {response_example}
    """

    chatgpt = ChatGPT(model=gpt_model, prompt=prompt)
    resp_text = await chatgpt.get_response_text(
        f"'{word_input=}', '{input_lang_iso2=}', '{target_lang_iso2=}', '{context_input=}'")
    resp_json = json.loads(resp_text)
    transl_word_out_ser = TranslWordOutSerializer(word_output=resp_json['word_output'],
                                                  word_pos=resp_json['word_pos'],
                                                  context_output=resp_json['context_output'],
                                                  input_lang_iso2=input_lang_iso2,
                                                  target_lang_iso2=target_lang_iso2
                                                  )
    return transl_word_out_ser


async def translate_phrase_chatgpt(
        phrase_input: str,
        input_language_iso2_name: LanguagesISO2NamesEnum,
        target_language_iso2_name: LanguagesISO2NamesEnum,
        model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
) -> dict:
    """Translates text to the specified language using OpenAI's GPT-4 model"""
    assert len(phrase_input.split()) > 1, "this method is for multiple words translation only"
    response_phrase_transl_example = """
    {
      "phrase_output": "..."
    }
    """
    prompt = f"""You are phrase translator.
    I provide you input_text, input_language_iso2_name, target_language_iso2_name, 
    Your response must be exactly as the following example:
    {response_phrase_transl_example}
    Punctuation, capitalization must be the same as in provided input. If input was in quotes - screen them.
    """

    chatgpt = ChatGPT(model=model, prompt=prompt)
    resp_text = await chatgpt.get_response_text(
        f"'{phrase_input=}', '{input_language_iso2_name=}', '{target_language_iso2_name=}'")
    return json.loads(resp_text)
