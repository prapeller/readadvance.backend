from core.enums import RequestMethodsEnum, ChatGPTModelsEnum
from db.serializers.translations import TranslNlpAPIOutSerializer, TranslWordOutSerializer, TranslNlpAPIInSerializer, \
    TranslWordInSerializer
from services.inter_service_manager.inter_service_manager import InterServiceManager
from services.translator.chatgpt_helpers import translate_word_chatgpt


async def translate_word_with_gpt(
        transl_word_in_ser: TranslWordInSerializer,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_3_5,
) -> TranslWordOutSerializer:
    transl_gpt_ser = await translate_word_chatgpt(
        word_input=transl_word_in_ser.word_input,
        input_lang_iso2=transl_word_in_ser.input_lang_iso2,
        target_lang_iso2=transl_word_in_ser.target_lang_iso2,
        context_input=transl_word_in_ser.context_input,
        gpt_model=gpt_model,
    )
    return transl_gpt_ser


async def translate_with_nlp_api(
        transl_in_ser: TranslNlpAPIInSerializer,
) -> TranslNlpAPIOutSerializer:
    inter_serv_manager = InterServiceManager()
    url, code, resp = await inter_serv_manager.send_request_to_nlp(RequestMethodsEnum.post,
                                                                   'translations/translate',
                                                                   transl_in_ser.model_dump())
    transl_out_ser = TranslNlpAPIOutSerializer.model_validate_json(resp)
    return transl_out_ser
