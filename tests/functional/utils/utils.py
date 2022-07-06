from contextlib import asynccontextmanager

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
