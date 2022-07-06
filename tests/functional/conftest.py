import asyncio
from contextlib import suppress
from dataclasses import dataclass

import aiohttp
import elasticsearch
import pytest
from config import config
from data.data import films, genres, persons
from data.indexes import ES_GENRES_SCHEMA, ES_MOVIES_SCHEMA, ES_PERSONS_SCHEMA
from data.models import BaseModel
from elasticsearch import AsyncElasticsearch
from utils.utils import elastic_connection, redis_connection


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def elastic_client():
    async with elastic_connection(hosts=[config.ELASTIC_PATH]) as elastic:
        yield elastic


@pytest.fixture(scope="session")
async def redis_client():
    async with redis_connection(
        url=f"{config.REDIS_PATH}", encoding="utf-8", decode_responses=True
    ) as redis:
        yield redis


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@dataclass
class Response:
    body: dict
    status: int


@pytest.fixture(scope="session")
async def client(session):
    class Client:
        path = "http://localhost:80" + "/api/v1"

        async def _make_request(self, method: str, path: str, **kwargs):
            path = self.path + path
            async with getattr(session, method)(path, **kwargs) as response:
                return Response(body=await response.json(), status=response.status)

        async def get(self, path, **kwargs):
            return await self._make_request("get", path, **kwargs)

        async def post(self, path, **kwargs):
            return await self._make_request("post", path, **kwargs)

        async def put(self, path, **kwargs):
            return await self._make_request("put", path, **kwargs)

        async def patch(self, path, **kwargs):
            return await self._make_request("patch", path, **kwargs)

    return Client()


@pytest.fixture
async def populate_elastic(elastic_client):
    await asyncio.gather(
        clear_and_populate_index(
            elastic_client, config.ELASIC_INDEX_NAME_MOVIES, ES_MOVIES_SCHEMA, films
        ),
        clear_and_populate_index(
            elastic_client, config.ELASIC_INDEX_NAME_GENRES, ES_GENRES_SCHEMA, genres
        ),
        clear_and_populate_index(
            elastic_client, config.ELASIC_INDEX_NAME_PERSONS, ES_PERSONS_SCHEMA, persons
        ),
    )


@pytest.fixture
async def clear_cache(redis_client):
    await redis_client.flushdb()


async def clear_index(elastic_client: AsyncElasticsearch, index_name: str) -> None:
    with suppress(elasticsearch.NotFoundError):
        await elastic_client.indices.delete(index=index_name)


async def clear_indexes(elastic_client: AsyncElasticsearch) -> None:
    await asyncio.gather(
        *[
            clear_index(elastic_client, index_name)
            for index_name in [
                config.ELASIC_INDEX_NAME_MOVIES,
                config.ELASIC_INDEX_NAME_GENRES,
                config.ELASIC_INDEX_NAME_PERSONS,
            ]
        ]
    )


async def clear_and_populate_index(
    elastic_client: AsyncElasticsearch,
    index_name: str,
    index_schema: dict,
    items: list[BaseModel],
) -> None:
    await clear_index(elastic_client, index_name)
    await elastic_client.indices.create(index=index_name, **index_schema)
    await asyncio.gather(
        *[
            elastic_client.index(
                index=index_name,
                id=str(item.id),
                document=item.to_dict(),
                refresh="wait_for",
            )
            for item in items
        ]
    )
