import asyncio
from contextlib import suppress

from aioredis.exceptions import ConnectionError
from config import config
from utils.base import redis_connection


async def wait_for_redis():
    async with redis_connection(
        url=f"redis://{config.REDIS_PATH}", encoding="utf-8", decode_responses=True
    ) as redis:
        while True:
            with suppress(ConnectionError):
                if await redis.ping():
                    return True
            print("waiting for redis")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(wait_for_redis())
