import fastapi as fa

from core.enums import ChatGPTModelsEnum
from db.serializers.translations import TranslWordInSerializer
from services.translator.translator import translate_word_with_gpt

router = fa.APIRouter()


@router.post("/translate-word-with-gpt")
async def translations_translate_word_with_gpt(
        transl_word_in_ser: TranslWordInSerializer,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_3_5,
):
    """get word translation with chatgpt"""
    return await translate_word_with_gpt(transl_word_in_ser, gpt_model)
