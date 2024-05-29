from abc import ABC, abstractmethod
from pathlib import Path

import backoff
import orjson
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError

from core import config
from core.config import settings
from core.logger_config import setup_logger
from core.shared import custom_serialize, singleton_decorator

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class Cache(ABC):

    @abstractmethod
    def set_cache(self, cache_key, data):
        pass

    @abstractmethod
    def get_cache(self, cache_key):
        pass


@singleton_decorator
class RedisCache(Cache):

    def __init__(self):
        self.redis: Redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    @backoff.on_exception(backoff.constant, (ConnectionError, RedisError), interval=1, max_tries=5)
    async def set_cache(self, cache_key: str, obj: dict):
        obj_dict = await custom_serialize(obj)
        data: bytes = orjson.dumps(obj_dict)
        try:
            await self.redis.set(cache_key, data, config.REDIS_CACHE_EXPIRES_IN_SECONDS)
            logger.debug('set by {}, {}'.format(cache_key, str(data)[:10]))
        except (TypeError, RedisError) as e:
            logger.error("can't set by {}, {}".format(cache_key, e))

    @backoff.on_exception(backoff.constant, (ConnectionError, RedisError), interval=1, max_tries=5)
    async def get_cache(self, cache_key: str) -> dict | list | None:
        try:
            data: bytes = await self.redis.get(cache_key)
            if data is not None:
                data: dict | list = orjson.loads(data)
            return data
        except RedisError as e:
            logger.error("can't get by {}, {}".format(cache_key, e))
            return None

    async def close(self):
        await self.redis.close()
