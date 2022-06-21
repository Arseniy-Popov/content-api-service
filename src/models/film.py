from uuid import UUID

from models.base import BaseDBModel


class PersonShort(BaseDBModel):
    id: UUID
    name: str


class GenreShort(BaseDBModel):
    id: UUID
    name: str


class Film(BaseDBModel):
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None

    genres: list[GenreShort]

    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]

    genres_names: list[str]

    actors_names: list[str]
    writers_names: list[str]
    directors_names: list[str]
