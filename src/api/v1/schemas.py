from typing import Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from models.base import BaseDBModel
from models.person import Person

BaseSchemaType = TypeVar("BaseSchemaType", bound="BaseSchema")


class BaseSchema(BaseModel):
    @classmethod
    def from_model(cls: Type[BaseSchemaType], model: BaseDBModel) -> BaseSchemaType:
        return cls(**model.dict())


class GenreSchema(BaseSchema):
    id: UUID
    name: str


class PersonShortSchema(BaseSchema):
    id: UUID
    name: str


class PersonSchema(BaseSchema):
    id: UUID
    name: str
    actor: list[UUID]
    writer: list[UUID]
    director: list[UUID]

    @classmethod
    def from_model(cls, person: Person) -> "PersonSchema":
        return cls(
            id=person.id,
            name=person.name,
            actor=[x.id for x in person.actor],
            writer=[x.id for x in person.writer],
            director=[x.id for x in person.director],
        )


class FilmShortSchema(BaseSchema):
    id: UUID
    title: str
    imdb_rating: float | None


class FilmLongSchema(BaseSchema):
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None

    genres: list[GenreSchema]

    actors: list[PersonShortSchema]
    writers: list[PersonShortSchema]
    directors: list[PersonShortSchema]


class PersonsFilmsSchema(BaseSchema):
    actor: list[FilmShortSchema]
    writer: list[FilmShortSchema]
    director: list[FilmShortSchema]
