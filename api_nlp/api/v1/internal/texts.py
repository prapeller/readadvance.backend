import fastapi as fa

from db.serializers.text import TextSerializer, TextReadWordsSerializer
from services.nlp_manager.nlp_manager import NLPManager

router = fa.APIRouter()


@router.post("/{text_uuid}", response_model=TextReadWordsSerializer)
async def texts_lemmatizate(
        text_ser: TextSerializer,
):
    nlp_manager = NLPManager()
    return nlp_manager.get_lemm_text_words(text_ser)
