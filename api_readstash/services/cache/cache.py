from abc import ABC, abstractmethod
from pathlib import Path

import orjson
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core import config
from core.logger_config import setup_logger
from core.shared import custom_serialize

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class Cache(ABC):

    @abstractmethod
    def set_cache(self, cache_key, data):
        pass

    @abstractmethod
    def get_cache(self, cache_key):
        pass


class RedisCache(Cache):

    def __init__(self, redis: Redis):
        self.redis: Redis = redis

    async def set_cache(self, cache_key: str, obj: dict):
        obj_dict = await custom_serialize(obj)
        data: bytes = orjson.dumps(obj_dict)
        try:
            await self.redis.set(cache_key, data, config.REDIS_CACHE_EXPIRES_IN_SECONDS)
            logger.debug('set by {}, {}'.format(cache_key, str(data)[:10]))
        except (TypeError, RedisError) as e:
            logger.error("can't set by {}, {}".format(cache_key, e))

    async def get_cache(self, cache_key: str) -> dict | list | None:
        try:
            data: bytes = await self.redis.get(cache_key)
            if data is not None:
                data: dict | list = orjson.loads(data)
            return data
        except RedisError as e:
            logger.error("can't get by {}, {}".format(cache_key, e))
            return None


redis_cache: RedisCache | None = None


def redis_cache_dependency():
    return redis_cache
