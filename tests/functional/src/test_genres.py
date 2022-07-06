import uuid

import pytest
from conftest import clear_indexes
from data.data import genre_sci_fi, genres

from tests.functional.data.models import Genre


class TestList:
    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.asyncio
    async def test_list(
        self, populate_elastic, clear_cache, client, elastic_client, test_cache: bool
    ):
        async def _request():
            return await client.get("/genres")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == 200
        assert response.body == [
            {"id": str(genre.id), "name": genre.name} for genre in genres
        ]


class TestRetrieve:
    @pytest.mark.parametrize("test_cache", [False, True])
    @pytest.mark.parametrize(
        "id, status, result",
        [
            (genre_sci_fi.id, 200, genre_sci_fi),
            (uuid.uuid4(), 404, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_retrieve(
        self,
        populate_elastic,
        clear_cache,
        client,
        elastic_client,
        test_cache: bool,
        id: str,
        status: int,
        result: Genre | None,
    ):
        async def _request():
            return await client.get(f"/genres/{id}")

        if test_cache:
            await _request()
            await clear_indexes(elastic_client)

        response = await _request()

        assert response.status == status
        if status == 200:
            assert response.body == {"id": str(result.id), "name": result.name}
