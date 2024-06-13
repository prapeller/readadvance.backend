import hashlib
import hmac
import time

import fastapi as fa
from starlette.middleware.base import BaseHTTPMiddleware

from core import config
from core.config import settings
from core.logger_config import setup_logger

logger = setup_logger('security')


async def generate_timestamp_hmac() -> tuple[int, str]:
    timestamp = int(time.time())  # Current Unix timestamp
    signature = hmac.new(settings.INTER_SERVICE_SECRET.encode(), str(timestamp).encode(), hashlib.sha256).hexdigest()
    return timestamp, signature


class VerifyHMACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fa.Request, call_next):
        if 'api/v1/internal' in request.url.path:
            logger.debug(f'{request.client.host=}, {request.url.path=}, {request.method=}, {request.headers=}')
            try:
                received_signature = request.headers.get('X-HMAC-Signature')
                received_timestamp_str = request.headers.get('X-Timestamp')
                if received_timestamp_str is None or received_signature is None:
                    detail = f'necessary headers not provided: {received_timestamp_str=}, {received_signature=}'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_403_FORBIDDEN,
                                                     content={'detail': detail})
                received_timestamp = int(received_timestamp_str)
                current_timestamp = int(time.time())
                if abs(current_timestamp - received_timestamp) > config.ACCEPTABLE_HMAC_TIME_SECONDS:
                    detail = f'{received_timestamp=:} doesnt feet timeframe'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_403_FORBIDDEN,
                                                     content={'detail': detail})

                expected_signature = hmac.new(settings.INTER_SERVICE_SECRET.encode(), str(received_timestamp).encode(),
                                              hashlib.sha256).hexdigest()
                if not hmac.compare_digest(expected_signature, received_signature):
                    detail = f'{received_signature=:} doesnt match {expected_signature=:}'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_403_FORBIDDEN,
                                                     content={'detail': detail})
            except Exception as e:
                return fa.responses.JSONResponse(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 content={'detail': str(e)})

        response = await call_next(request)
        return response
