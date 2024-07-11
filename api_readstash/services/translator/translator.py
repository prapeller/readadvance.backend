from core.constants import PARTS_OF_SPEECH
from core.enums import RequestMethodsEnum, ChatGPTModelsEnum
from db.serializers.analyses import AnalysesOutSerializer, AnalysesInSerializer
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


async def translate_word_with_nlp_api(
        transl_word_in_ser: TranslWordInSerializer,
) -> TranslWordOutSerializer:
    context_output = None
    inter_serv_manager = InterServiceManager()
    transl_word_in_nlp_ser = TranslNlpAPIInSerializer(
        text_input=transl_word_in_ser.word_input,
        input_lang_iso2=transl_word_in_ser.input_lang_iso2,
        target_lang_iso2=transl_word_in_ser.target_lang_iso2,
    )
    url, code, resp = await inter_serv_manager.send_request_to_nlp(RequestMethodsEnum.post,
                                                                   'translations/translate',
                                                                   transl_word_in_nlp_ser.model_dump())
    transl_word_out_nlp_ser = TranslNlpAPIOutSerializer.model_validate_json(resp)

    an_in_ser = AnalysesInSerializer(content=transl_word_in_ser.word_input, iso2=transl_word_in_ser.input_lang_iso2)
    url, code, resp = await inter_serv_manager.send_request_to_nlp(RequestMethodsEnum.post,
                                                                   'analyses/analyze',
                                                                   an_in_ser.model_dump())
    an_res = AnalysesOutSerializer.model_validate_json(resp)

    if transl_word_in_ser.context_input is not None:
        transl_in_context_ser = TranslNlpAPIInSerializer(
            text_input=transl_word_in_ser.context_input,
            input_lang_iso2=transl_word_in_ser.input_lang_iso2,
            target_lang_iso2=transl_word_in_ser.target_lang_iso2,
        )
        url, code, resp = await inter_serv_manager.send_request_to_nlp(RequestMethodsEnum.post,
                                                                       'translations/translate',
                                                                       transl_in_context_ser.model_dump())
        context_transl_res = TranslNlpAPIOutSerializer.model_validate_json(resp)
        context_output = context_transl_res.text_output

    return TranslWordOutSerializer(
        word_output=transl_word_out_nlp_ser.text_output,
        word_pos=PARTS_OF_SPEECH[transl_word_in_ser.target_lang_iso2].get(an_res.words[0]['pos']),
        context_output=context_output,
        input_lang_iso2=transl_word_out_nlp_ser.input_lang_iso2,
        target_lang_iso2=transl_word_out_nlp_ser.target_lang_iso2,
    )
