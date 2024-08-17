import fastapi as fa

from db.serializers.translations import TranslInSerializer, TranslOutSerializer
from services.translator_marianmt.translator_marianmt import TranslatorMarianMT

router = fa.APIRouter()


@router.post("/translate", response_model=TranslOutSerializer)
async def translate(
        tran_ser: TranslInSerializer,
):
    marian_manager = TranslatorMarianMT()
    return await marian_manager.translate(tran_ser)
