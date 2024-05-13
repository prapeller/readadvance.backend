import fastapi as fa
from starlette.middleware.base import BaseHTTPMiddleware


class CatchAssertionErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fa.Request, call_next):
        try:
            response = await call_next(request)
        except AssertionError as e:
            detail = str(e)
            response = fa.responses.ORJSONResponse(status_code=400, content={"detail": detail})
        return response
