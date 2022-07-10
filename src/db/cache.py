import json
from abc import abstractmethod
from typing import Any, Protocol

from aioredis import Redis

redis_client: Redis | None = None


class CacheAdapterProtocol(Protocol):
    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        ...

    @abstractmethod
    async def get(self, key: str) -> list | dict | None:
        ...


class RedisAdapter(CacheAdapterProtocol):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, value: Any) -> None:
        value = json.dumps(value)
        await self.redis.set(key, value)

    async def get(self, key: str) -> list | dict | None:
        if value := await self.redis.get(key):
            return json.loads(value)
        return None


async def get_cache() -> CacheAdapterProtocol:
    return RedisAdapter(redis_client)
