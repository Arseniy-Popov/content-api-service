from uuid import UUID

from models.base import BaseDBModel


class Genre(BaseDBModel):
    id: UUID
    name: str
