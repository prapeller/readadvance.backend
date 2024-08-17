import fastapi as fa
import uvicorn
from api.v1.internal import (
    analyses as v1_internal_analyses,
    translations as v1_internal_translations,
)
from contextlib import asynccontextmanager
from core.config import settings
from core.middlewares import CatchAssertionErrorMiddleware
from core.security import VerifyHMACMiddleware
from fastapi.responses import ORJSONResponse
from services.analyzer_stanza.analyzer_stanza import AnalyzerStanza
from services.translator_marianmt.translator_marianmt import TranslatorMarianMT


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup
    AnalyzerStanza()
    TranslatorMarianMT()

    # shutdown
    yield


app = fa.FastAPI(
    title=settings.PROJECT_NAME,
    # swagger_ui_init_oauth={},
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(CatchAssertionErrorMiddleware)  # noqa
# app.add_middleware(VerifyHMACMiddleware)  # noqa

v1_router_internal = fa.APIRouter(prefix='/internal')
v1_router_internal.include_router(v1_internal_analyses.router, prefix='/analyses', tags=['internal'])
v1_router_internal.include_router(v1_internal_translations.router, prefix='/translations', tags=['internal'])

app.include_router(v1_router_internal, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_NLP_HOST, port=settings.API_NLP_PORT, reload=True)
