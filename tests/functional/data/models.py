import uuid
from dataclasses import asdict, dataclass, field
from typing import ClassVar, Protocol
from uuid import UUID


class BaseModel(Protocol):
    id: ClassVar[UUID]

    def to_dict(self):
        return asdict(self)


@dataclass(kw_only=True)
class Genre(BaseModel):
    id: UUID = field(default_factory=uuid.uuid4)
    name: str


@dataclass(kw_only=True)
class FilmShort(BaseModel):
    id: UUID = field(default_factory=uuid.uuid4)
    title: str


@dataclass(kw_only=True)
class PersonShort(BaseModel):
    id: UUID = field(default_factory=uuid.uuid4)
    name: str


@dataclass(kw_only=True)
class Person(BaseModel):
    id: UUID = field(default_factory=uuid.uuid4)
    full_name: str
    actor: list[FilmShort] = field(default_factory=list)
    writer: list[FilmShort] = field(default_factory=list)
    director: list[FilmShort] = field(default_factory=list)


@dataclass(kw_only=True)
class Film(BaseModel):
    id: UUID = field(default_factory=uuid.uuid4)
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genres: list[Genre] = field(default_factory=list)
    actors: list[Person] = field(default_factory=list)
    writers: list[Person] = field(default_factory=list)
    directors: list[Person] = field(default_factory=list)
    genres_names: list = field(default_factory=list)
    actors_names: list = field(default_factory=list)
    writers_names: list = field(default_factory=list)
    directors_names: list = field(default_factory=list)

    def __post_init__(self, *args, **kwargs):
        self.genres_names = [x.name for x in self.genres]

        for person in self.actors:
            person.actor.append(FilmShort(id=self.id, title=self.title))
        for person in self.writers:
            person.writer.append(FilmShort(id=self.id, title=self.title))
        for person in self.directors:
            person.director.append(FilmShort(id=self.id, title=self.title))

        self.actors_names = [x.full_name for x in self.actors]
        self.writers_names = [x.full_name for x in self.writers]
        self.directors_names = [x.full_name for x in self.directors]

        self.actors = [PersonShort(id=x.id, name=x.full_name) for x in self.actors]
        self.writers = [PersonShort(id=x.id, name=x.full_name) for x in self.writers]
        self.directors = [
            PersonShort(id=x.id, name=x.full_name) for x in self.directors
        ]
