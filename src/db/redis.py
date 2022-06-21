import json
from typing import Any

from aioredis import Redis

redis: Redis | None = None


async def get_redis() -> Redis | None:
    return redis


class RedisAdapter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, value: Any) -> None:
        value = json.dumps(value)
        await self.redis.set(key, value)

    async def get(self, key: str) -> list | dict | None:
        if value := await self.redis.get(key):
            return json.loads(value)
        return None
