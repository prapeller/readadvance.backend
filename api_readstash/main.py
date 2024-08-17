import fastapi as fa
import uvicorn
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse

from api.v1.auth import (
    postgres as v1_auth_postgres,
    users as v1_auth_users,
    words as v1_auth_words,
    texts as v1_auth_texts,
    translations as v1_auth_translations,
)
from api.v1.public import (
    languages as v1_public_languages,
    words as v1_public_words,
    # translations as v1_public_translations,
)
from core import config
from core.config import settings
from core.middlewares import CatchAssertionErrorMiddleware
from core.security import current_user_dependency, VerifyHMACMiddleware
from db import init_models
from scripts.recreate import recreate_test_data
from services.cache.cache import RedisCache


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # startup

    init_models()
    if config.DEBUG:
        await recreate_test_data()

    # shutdown
    yield
    await RedisCache().close()


app = fa.FastAPI(
    title=settings.PROJECT_NAME,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.KEYCLOAK_CLIENT_ID,
    },
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(CatchAssertionErrorMiddleware)  # noqa
app.add_middleware(VerifyHMACMiddleware)  # noqa

v1_router_auth = fa.APIRouter(
    dependencies=[fa.Depends(current_user_dependency)],
)
v1_router_auth.include_router(v1_auth_postgres.router, prefix='/postgres', tags=['postgres'])
v1_router_auth.include_router(v1_auth_users.router, prefix='/users', tags=['users'])
v1_router_auth.include_router(v1_auth_words.router, prefix='/words', tags=['words'])
v1_router_auth.include_router(v1_auth_texts.router, prefix='/texts', tags=['texts'])
v1_router_auth.include_router(v1_auth_translations.router, prefix='/translations', tags=['translations'])

v1_router_public = fa.APIRouter(prefix='/public')
v1_router_public.include_router(v1_public_languages.router, prefix='/languages', tags=['languages'])
v1_router_public.include_router(v1_public_words.router, prefix='/words', tags=['words'])
# v1_router_public.include_router(v1_public_translations.router, prefix='/translations', tags=['translations'])

app.include_router(v1_router_auth, prefix="/api/v1")
app.include_router(v1_router_public, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_READSTASH_HOST, port=settings.API_READSTASH_PORT, reload=True)
