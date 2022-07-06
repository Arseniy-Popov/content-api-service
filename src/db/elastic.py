from abc import abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Protocol
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Search

from db.redis import CacheProtocol

elastic: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch:
    return elastic


@dataclass
class ElasticSearchResult:
    num_hits: int
    hits: list[dict]
    docs: list[dict]


class ElasticIndexes(str, Enum):
    MOVIES = "movies"
    PERSONS = "persons"
    GENRES = "genres"


class ElasticAdapterProtocol(Protocol):
    @abstractmethod
    async def get(self, index: str, id: UUID) -> dict | None:
        ...

    @abstractmethod
    async def search(self, search: Search) -> ElasticSearchResult:
        ...


class ElasticAdapter(ElasticAdapterProtocol):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get(self, index: str, id: UUID) -> dict | None:
        try:
            result = await self.elastic.get(index=index, id=str(id))
        except NotFoundError:
            return None
        return result["_source"]

    async def search(self, search: Search) -> ElasticSearchResult:
        result = await self.elastic.search(
            index=search._index, body=search.to_dict(), **search._params
        )
        return ElasticSearchResult(
            num_hits=result["hits"]["total"]["value"],
            hits=result["hits"]["hits"],
            docs=[x["_source"] for x in result["hits"]["hits"]],
        )


class CachedElasticDecorator(ElasticAdapterProtocol):
    def __init__(self, elastic: ElasticAdapterProtocol, cache: CacheProtocol, ttl: int):
        self.elastic = elastic
        self.cache = cache
        self.ttl = ttl

    async def get(self, index: str, id: UUID) -> dict | None:
        key = str((index, id))
        if cached := await self.cache.get(key):
            return cached
        data = await self.elastic.get(index, id)
        await self.cache.set(key, data)
        return data

    async def search(self, search: Search) -> ElasticSearchResult:
        key = str((search._index, search.to_dict(), search._params))
        if cached := await self.cache.get(key):
            return ElasticSearchResult(**cached)
        data = await self.elastic.search(search)
        await self.cache.set(key, asdict(data))
        return data
