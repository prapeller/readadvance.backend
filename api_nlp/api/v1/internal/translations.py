import fastapi as fa

from db.serializers.translations import TranslInSerializer, TranslOutSerializer
from services.marianmt_manager.marianmt_manager import MarianMTManager

router = fa.APIRouter()


@router.post("/translate", response_model=TranslOutSerializer)
async def translate(
        tran_ser: TranslInSerializer,
):
    marian_manager = MarianMTManager()
    return await marian_manager.translate(tran_ser)
