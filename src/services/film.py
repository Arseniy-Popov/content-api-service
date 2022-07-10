from functools import lru_cache
from uuid import UUID

from elasticsearch_dsl import Q, Search
from fastapi import Depends

from core.config import config
from db.cache import CacheAdapterProtocol, get_cache
from db.elastic import (
    CachedElasticDecorator,
    ElasticAdapterProtocol,
    ElasticIndexes,
    get_elastic,
)
from models.film import Film
from services.base import paginate


class FilmService:
    def __init__(self, cache: CacheAdapterProtocol, elastic: ElasticAdapterProtocol):
        self.elastic = CachedElasticDecorator(elastic, cache, config.FILMS_CACHE_EXPIRE)

    async def retrieve(self, film_id: UUID) -> Film | None:
        if film := await self.elastic.get(index=ElasticIndexes.MOVIES, id=film_id):
            return Film(**film)
        return None

    async def search(
        self,
        query_string: str | None,
        sort_field: str | None,
        genre_id: UUID | None,
        page_number: int,
        page_size: int,
    ) -> tuple[list[Film], int]:
        search = Search(index=ElasticIndexes.MOVIES)
        search.query = Q("bool")

        if sort_field:
            search = search.sort(sort_field)
        if genre_id:
            search.query.filter = [
                Q(
                    "nested",
                    path="genres",
                    query=Q("bool", filter=Q("term", genres__id=genre_id)),
                )
            ]
        if query_string:
            search.query.must = [
                Q(
                    "multi_match",
                    query=query_string,
                    fields=[
                        "title^4",
                        "description^2",
                        "actors_names",
                        "writers_names",
                        "directors_names",
                    ],
                    fuzziness=2,
                )
            ]
        search = paginate(search, page_number, page_size)

        results = await self.elastic.search(search)

        return (
            [Film(**item) for item in results.docs],
            results.num_hits,
        )


@lru_cache()
def get_film_service(
    cache: CacheAdapterProtocol = Depends(get_cache),
    elastic: ElasticAdapterProtocol = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, elastic)
