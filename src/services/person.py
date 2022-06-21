from functools import lru_cache
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import Terms
from fastapi import Depends

from core.config import config
from db.elastic import (
    CachedElasticDecorator,
    ElasticAdapter,
    ElasticIndexes,
    get_elastic,
)
from db.redis import RedisAdapter, get_redis
from models.film import Film
from models.person import FilmShort, Person, PersonsFilms
from services.base import paginate


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = CachedElasticDecorator(
            ElasticAdapter(elastic),
            RedisAdapter(self.redis),
            config.GENRES_CACHE_EXPIRE,
        )

    async def retrieve(self, id: UUID) -> Person | None:
        if not (person := await self.elastic.get(index=ElasticIndexes.PERSONS, id=id)):
            return None
        person = Person(**person)
        return person

    async def search(
        self, query_string: str, page_number: int, page_size: int
    ) -> tuple[list[Person], int]:
        search = Search(index=ElasticIndexes.PERSONS)
        search.query = Q("match", full_name=query_string)
        search = paginate(search, page_number, page_size)

        results = await self.elastic.search(search)

        return (
            [Person(**doc) for doc in results.docs],
            results.num_hits,
        )

    async def list_movies(self, person_id: UUID) -> PersonsFilms | None:
        if not (person := await self.retrieve(person_id)):
            return None
        actor_film_ids = [film.id for film in person.actor]
        writer_film_ids = [film.id for film in person.writer]
        director_film_ids = [film.id for film in person.director]

        search = Search(index=ElasticIndexes.MOVIES)
        search.query = Terms(id=actor_film_ids + writer_film_ids + director_film_ids)
        search = search[0:10000]

        results = await self.elastic.search(search)

        films = [Film(**doc) for doc in results.docs]
        film_id_2_film = {film.id: film for film in films}

        return PersonsFilms(
            actor=[FilmShort(**film_id_2_film[id].dict()) for id in actor_film_ids],
            writer=[FilmShort(**film_id_2_film[id].dict()) for id in writer_film_ids],
            director=[
                FilmShort(**film_id_2_film[id].dict()) for id in director_film_ids
            ],
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
