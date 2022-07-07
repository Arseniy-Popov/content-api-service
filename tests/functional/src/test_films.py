from uuid import UUID, uuid4

import pytest
from config import config
from conftest import clear_and_populate_index, clear_index, clear_indexes
from data.data import film_2
from data.indexes import ES_MOVIES_SCHEMA
from data.models import Film, Genre, Person


class TestSearch:
    """
    Test that multiple fields are searched with priority for Title.
    """

    film_1 = Film(title="Star Wars", imdb_rating=7.1)
    film_2 = Film(title="Expanse", imdb_rating=7.3, description="Star Wars")
    film_3 = Film(
        title="Expanse 2", imdb_rating=7.4, actors=[Person(full_name="Star Wars")]
    )
    film_4 = Film(
        title="Expanse 2", imdb_rating=7.4, writers=[Person(full_name="Star Wars")]
    )
    film_5 = Film(
        title="Expanse 2", imdb_rating=7.4, directors=[Person(full_name="Star Wars")]
    )

    @pytest.fixture(autouse=True)
    async def setup(self, clear_cache):
        pass

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "films",
        [
            [film_1, film_2],
            [film_1, film_3],
            [film_1, film_4],
            [film_1, film_5],
            [film_2, film_3],
            [film_2, film_4],
            [film_2, film_5],
        ],
    )
    @pytest.mark.asyncio
    async def test_search(
        self, client, elastic_client, films: list[Film], test_cache: bool
    ):
        await clear_and_populate_index(
            elastic_client,
            config.ELASIC_INDEX_NAME_MOVIES,
            ES_MOVIES_SCHEMA,
            films,
        )

        async def _request():
            return await client.get(f"/films/search", params={"query": "Star was"})

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
                    "id": str(x.id),
                    "title": x.title,
                    "imdb_rating": x.imdb_rating,
                }
                for x in films
            ],
        }


class TestSearchPaginate:
    films = [
        Film(title="Star Wars"),
        Film(title="Star Wars"),
        Film(title="Sta Was"),
        Film(title="Sta Was"),
    ]

    @pytest.fixture(autouse=True)
    async def setup(self, clear_cache, elastic_client):
        await clear_and_populate_index(
            elastic_client,
            config.ELASIC_INDEX_NAME_MOVIES,
            ES_MOVIES_SCHEMA,
            self.films,
        )

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "page_number, page_size, pages_count, status, result, titles",
        [
            # first page
            (1, 2, 2, 200, True, ["Star Wars", "Star Wars"]),
            # second page
            (2, 2, 2, 200, True, ["Sta Was", "Sta Was"]),
            # more items on page than results
            (1, 5, 1, 200, True, ["Star Wars", "Star Wars", "Sta Was", "Sta Was"]),
            # invalid pagination arguments
            (0, 2, None, 422, False, None),
            (1, 0, None, 422, False, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_search_paginate(
        self,
        client,
        elastic_client,
        page_number: int,
        result: bool,
        titles: list[str],
        status: int,
        page_size: int,
        pages_count: int,
        test_cache: bool,
    ):
        async def _request():
            return await client.get(
                f"/films/search",
                params={
                    "query": "Star Wars",
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
            assert [x["title"] for x in response.body["results"]] == titles
        else:
            assert "results" not in response.body


class TestList:
    genre_1 = Genre(name="genre 1")
    genre_2 = Genre(name="genre 2")
    film_1 = Film(title="film 1", imdb_rating=1.2, genres=[genre_1])
    film_2 = Film(title="film 2", imdb_rating=1.3, genres=[genre_1, genre_2])
    film_3 = Film(title="film 3", imdb_rating=1.4, genres=[genre_1])
    film_4 = Film(title="film 4", imdb_rating=1.5, genres=[genre_2])
    films = [film_1, film_2, film_3, film_4]

    @pytest.fixture(autouse=True)
    async def setup(self, clear_cache, elastic_client):
        await clear_and_populate_index(
            elastic_client,
            config.ELASIC_INDEX_NAME_MOVIES,
            ES_MOVIES_SCHEMA,
            self.films,
        )

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "genre, sort, status, results",
        [
            # no sort of genre filter
            (None, None, 200, [film_4, film_3, film_2, film_1]),
            # sort
            (None, "-imdb_rating", 200, [film_4, film_3, film_2, film_1]),
            (None, "imdb_rating", 200, [film_1, film_2, film_3, film_4]),
            # genre filter
            (genre_2.id, None, 200, [film_4, film_2]),
            # sort and genre filter
            (genre_2.id, "-imdb_rating", 200, [film_4, film_2]),
            (genre_2.id, "imdb_rating", 200, [film_2, film_4]),
            # genre w/o films
            (uuid4(), None, 200, []),
            # invalid sort directive
            (None, "rating", 422, []),
        ],
    )
    async def test_list(
        self,
        client,
        elastic_client,
        genre: UUID | None,
        sort: str | None,
        status: int,
        results: list[Film],
        test_cache: bool,
    ):
        params = {}
        if genre:
            params["filter[genre]"] = str(genre)
        if sort:
            params["sort"] = sort

        async def _request():
            return await client.get("/films", params=params)

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == status
        if status == 200:
            assert response.body == {
                "pages_count": 1,
                "page_number": 1,
                "results": [
                    {
                        "id": str(x.id),
                        "title": x.title,
                        "imdb_rating": x.imdb_rating,
                    }
                    for x in results
                ],
            }
        else:
            assert "results" not in response.body


class TestListPaginate:
    film_1 = Film(title="film 1", imdb_rating=1.2)
    film_2 = Film(title="film 2", imdb_rating=1.3)
    film_3 = Film(title="film 3", imdb_rating=1.4)
    film_4 = Film(title="film 4", imdb_rating=1.5)
    films = [film_1, film_2, film_3, film_4]

    @pytest.fixture(autouse=True)
    async def setup(self, clear_cache, elastic_client):
        await clear_and_populate_index(
            elastic_client,
            config.ELASIC_INDEX_NAME_MOVIES,
            ES_MOVIES_SCHEMA,
            self.films,
        )

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "page_number, page_size, pages_count, status, results",
        [
            # first page
            (1, 2, 2, 200, [film_4, film_3]),
            # second page
            (2, 2, 2, 200, [film_2, film_1]),
            # more items on page than results
            (1, 5, 1, 200, [film_4, film_3, film_2, film_1]),
            # invalid pagination arguments
            (0, 2, None, 422, None),
            (1, 0, None, 422, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_search_paginate(
        self,
        client,
        elastic_client,
        page_number: int,
        results: list[Film],
        status: int,
        page_size: int,
        pages_count: int,
        test_cache: bool,
    ):
        async def _request():
            return await client.get(
                f"/films",
                params={
                    "page[number]": page_number,
                    "page[size]": page_size,
                },
            )

        if test_cache:
            await _request()
            await clear_index(elastic_client, config.ELASIC_INDEX_NAME_MOVIES)

        response = await _request()
        assert response.status == status
        if status == 200:
            assert response.body["pages_count"] == pages_count
            assert response.body["page_number"] == page_number
            assert response.body["results"] == [
                {
                    "id": str(x.id),
                    "title": x.title,
                    "imdb_rating": x.imdb_rating,
                }
                for x in results
            ]
        else:
            assert "results" not in response.body


class TestRetrieve:
    @pytest.fixture(autouse=True)
    async def setup(self, clear_cache, populate_elastic):
        pass

    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_retrieve(self, client, elastic_client, test_cache: bool):
        async def _request():
            return await client.get(f"/films/{film_2.id}")

        if test_cache:
            await _request()
            await clear_index(elastic_client, config.ELASIC_INDEX_NAME_MOVIES)

        response = await _request()
        assert response.status == 200
        assert response.body == {
            "id": str(film_2.id),
            "title": film_2.title,
            "description": film_2.description,
            "imdb_rating": film_2.imdb_rating,
            "genres": [{"id": str(x.id), "name": x.name} for x in film_2.genres],
            "actors": [{"id": str(x.id), "name": x.name} for x in film_2.actors],
            "writers": [{"id": str(x.id), "name": x.name} for x in film_2.writers],
            "directors": [{"id": str(x.id), "name": x.name} for x in film_2.directors],
        }
