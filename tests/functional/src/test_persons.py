import uuid

import pytest
from config import config
from conftest import clear_and_populate_index, clear_indexes
from data.data import film_1, film_2, film_3, person_lucas
from data.indexes import ES_PERSONS_SCHEMA
from data.models import Person


class TestSearch:
    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_search(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get(
                f"/persons/search", params={"query": "georhe lucax"}
            )

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 200
        assert response.body == {
            "pages_count": 1,
            "page_number": 1,
            "results": [
                {
                    "id": str(person_lucas.id),
                    "name": person_lucas.full_name,
                    "actor": [str(x.id) for x in person_lucas.actor],
                    "writer": [str(x.id) for x in person_lucas.writer],
                    "director": [str(x.id) for x in person_lucas.director],
                },
            ],
        }

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "page_number, page_size, pages_count, status, result, names",
        [
            # first page
            (1, 2, 2, 200, True, ["John Cena", "John Cena"]),
            # second page
            (2, 2, 2, 200, True, ["Jon Cena", "Jon Cena"]),
            # more items on page than results
            (1, 5, 1, 200, True, ["John Cena", "John Cena", "Jon Cena", "Jon Cena"]),
            # invalid pagination arguments
            (0, 2, None, 422, False, None),
            (1, 0, None, 422, False, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_search_paginate(
        self,
        populate_elastic,
        clear_cache,
        client,
        elastic_client,
        page_number: int,
        result: bool,
        names: list[str],
        status: int,
        page_size: int,
        pages_count: int,
        test_cache: bool,
    ):
        persons = [
            Person(full_name="John Cena"),
            Person(full_name="John Cena"),
            Person(full_name="Jon Cena"),
            Person(full_name="Jon Cena"),
        ]

        await clear_and_populate_index(
            elastic_client, config.ELASIC_INDEX_NAME_PERSONS, ES_PERSONS_SCHEMA, persons
        )

        async def _request():
            return await client.get(
                f"/persons/search",
                params={
                    "query": "john",
                    "page[number]": page_number,
                    "page[size]": page_size,
                },
            )

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == status
        if result:
            assert response.body["pages_count"] == pages_count
            assert response.body["page_number"] == page_number
            assert [x["name"] for x in response.body["results"]] == names
        else:
            assert "results" not in response.body


class TestRetrieve:
    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_retrieve(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get(f"/persons/{person_lucas.id}")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 200
        assert response.body == {
            "id": str(person_lucas.id),
            "name": person_lucas.full_name,
            "actor": [str(x.id) for x in person_lucas.actor],
            "writer": [str(x.id) for x in person_lucas.writer],
            "director": [str(x.id) for x in person_lucas.director],
        }

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_retrieve_not_found(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get(f"/persons/{uuid.uuid4()}")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 404


class TestListPersonsFilms:
    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_list_films(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get(f"/persons/{person_lucas.id}/films")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 200
        assert response.body == {
            "actor": [
                {"id": str(x.id), "imdb_rating": x.imdb_rating, "title": x.title}
                for x in [film_3]
            ],
            "writer": [
                {"id": str(x.id), "imdb_rating": x.imdb_rating, "title": x.title}
                for x in [film_1, film_2]
            ],
            "director": [
                {"id": str(x.id), "imdb_rating": x.imdb_rating, "title": x.title}
                for x in [film_1, film_2]
            ],
        }

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_list_films_not_found(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get(f"/persons/{uuid.uuid4()}/films")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 404
