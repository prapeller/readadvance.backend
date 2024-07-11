import fastapi as fa

from db.serializers.analyses import AnalysesInSerializer, AnalysesOutSerializer
from services.stanza_manager.stanza_manager import StanzaManager

router = fa.APIRouter()


@router.post("/analyze", response_model=AnalysesOutSerializer)
async def analyze_content(
        an_in_ser: AnalysesInSerializer,
):
    nlp_manager = StanzaManager()
    return await nlp_manager.analyze(an_in_ser)
