import fastapi as fa

from db.serializers.analyses import AnalysesInSerializer, AnalysesOutSerializer
from services.analyzer_stanza.analyzer_stanza import AnalyzerStanza

router = fa.APIRouter()


@router.post("/analyze", response_model=AnalysesOutSerializer)
async def analyze_content(
        an_in_ser: AnalysesInSerializer,
):
    analyzer = AnalyzerStanza()
    return await analyzer.analyze(an_in_ser)
