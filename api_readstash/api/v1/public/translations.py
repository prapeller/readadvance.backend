import fastapi as fa

from core.enums import ChatGPTModelsEnum
from db.serializers.translations import TranslWordInSerializer
from services.translator.translator import translate_word_with_gpt, translate_word_with_nlp_api

# router = fa.APIRouter()

#
# @router.post("/translate-word-with-nlp-api")
# async def translations_translate_word_with_gpt(
#         transl_word_in_ser: TranslWordInSerializer,
# ):
#     """get word translation with nlp api"""
#     return await translate_word_with_nlp_api(transl_word_in_ser)
