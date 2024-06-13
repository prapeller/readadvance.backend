import traceback
from pathlib import Path

import httpx

from core.config import settings
from core.enums import RequestMethodsEnum
from core.logger_config import setup_logger
from core.security import generate_timestamp_hmac

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class InterServiceManager:
    async def __send_request_async(self,
                                   method: RequestMethodsEnum,
                                   url: str,
                                   json=None,
                                   data=None,
                                   params=None,
                                   headers: dict | None = None):
        """send request with httpx client"""
        try:
            async with httpx.AsyncClient() as client:
                if method == RequestMethodsEnum.get:
                    resp = await client.get(url, params=params, headers=headers)
                elif method == RequestMethodsEnum.delete:
                    resp = await client.delete(url, params=params, headers=headers)
                elif method == RequestMethodsEnum.post:
                    resp = await client.post(url, json=json, data=data, headers=headers)
                else:
                    resp = await client.put(url, json=json, data=data, headers=headers)
            return resp
        except Exception:
            logger.error(traceback.format_exc())
            raise

    async def send_request_to_nlp(self, method: RequestMethodsEnum,
                                  url_postfix: str,
                                  json=None,
                                  data=None,
                                  params=None) -> tuple[str, int, bytes]:
        base_url = f'http://{settings.API_NLP_HOST}:{settings.API_NLP_PORT}/api/v1/internal'
        url = f'{base_url}/{url_postfix}'
        timestamp, signature = await generate_timestamp_hmac()
        headers = {
            'X-HMAC-Signature': signature,
            'X-Timestamp': str(timestamp)
        }
        resp = await self.__send_request_async(method, url, json, data, params, headers)
        return '{0}://{1}{2}:{3}{4}'.format(*resp.request.url._uri_reference), resp.status_code, resp.content
