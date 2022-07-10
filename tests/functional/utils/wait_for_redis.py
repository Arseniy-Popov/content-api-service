import asyncio

from config import config
from utils.base import backoff, redis_connection


@backoff()
async def ping_redis():
    async with redis_connection(
        url=f"redis://{config.REDIS_PATH}", encoding="utf-8", decode_responses=True
    ) as redis:
        return await redis.ping()


if __name__ == "__main__":
    asyncio.run(ping_redis())
