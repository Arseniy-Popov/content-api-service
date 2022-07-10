import time
from contextlib import asynccontextmanager
from functools import wraps

import aioredis
from elasticsearch import AsyncElasticsearch


@asynccontextmanager
async def elastic_connection(**kwargs):
    elastic = AsyncElasticsearch(**kwargs)
    try:
        yield elastic
    finally:
        await elastic.close()


@asynccontextmanager
async def redis_connection(**kwargs):
    redis = await aioredis.from_url(**kwargs)
    try:
        yield redis
    finally:
        await redis.close()


def backoff(
    *,
    min_sleep_time: int = 1,
    max_sleep_time: int = 10,
    factor: int = 2,
):
    """
    Waits for a positive response for the decorated function, repeating the call on
    exceptions and negative responses.
    """

    def outer(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            iters = 0
            while True:
                try:
                    result = await func(*args, **kwargs)
                    if result:
                        return result
                except Exception:
                    pass
                finally:
                    sleep_time = min(min_sleep_time * factor**iters, max_sleep_time)
                    iters += 1
                    print(f"waiting for {func.__name__}")
                    time.sleep(sleep_time)

        return inner

    return outer
