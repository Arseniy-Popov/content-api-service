from uuid import UUID

from pydantic import Field

from models.base import BaseDBModel


class FilmShort(BaseDBModel):
    id: UUID
    title: str
    imdb_rating: float | None = None


class Person(BaseDBModel):
    id: UUID
    name: str = Field(alias="full_name")
    actor: list[FilmShort] = []
    writer: list[FilmShort] = []
    director: list[FilmShort] = []


class PersonsFilms(BaseDBModel):
    actor: list[FilmShort]
    writer: list[FilmShort]
    director: list[FilmShort]
