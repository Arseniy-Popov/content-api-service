from functools import lru_cache
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from core.config import config
from db.elastic import (
    CachedElasticDecorator,
    ElasticAdapter,
    ElasticIndexes,
    get_elastic,
)
from db.redis import RedisAdapter, get_redis
from models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = CachedElasticDecorator(
            ElasticAdapter(elastic),
            RedisAdapter(self.redis),
            config.GENRES_CACHE_EXPIRE,
        )

    async def list(self) -> list[Genre]:
        search = Search(index=ElasticIndexes.GENRES)
        search = search[0:1000]
        results = await self.elastic.search(search)
        return [Genre(**doc) for doc in results.docs]

    async def retrieve(self, id: UUID) -> Genre | None:
        if doc := await self.elastic.get(index=ElasticIndexes.GENRES, id=id):
            return Genre(**doc)
        return None


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
