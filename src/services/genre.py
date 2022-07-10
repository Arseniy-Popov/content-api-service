from functools import lru_cache
from uuid import UUID

from elasticsearch_dsl import Search
from fastapi import Depends

from core.config import config
from db.cache import CacheAdapterProtocol, get_cache
from db.elastic import (
    CachedElasticDecorator,
    ElasticAdapterProtocol,
    ElasticIndexes,
    get_elastic,
)
from models.genre import Genre


class GenreService:
    def __init__(self, cache: CacheAdapterProtocol, elastic: ElasticAdapterProtocol):
        self.elastic = CachedElasticDecorator(elastic, cache, config.FILMS_CACHE_EXPIRE)

    async def list(self) -> list[Genre]:
        search = Search(index=ElasticIndexes.GENRES)
        search = search[0:1000]
        search = search.sort("name.raw")
        results = await self.elastic.search(search)
        return [Genre(**doc) for doc in results.docs]

    async def retrieve(self, id: UUID) -> Genre | None:
        if doc := await self.elastic.get(index=ElasticIndexes.GENRES, id=id):
            return Genre(**doc)
        return None


@lru_cache()
def get_genre_service(
    cache: CacheAdapterProtocol = Depends(get_cache),
    elastic: ElasticAdapterProtocol = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, elastic)
