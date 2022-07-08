from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import Query
from pydantic.generics import GenericModel

ResponseModel = TypeVar("ResponseModel")


class PaginatedResponse(GenericModel, Generic[ResponseModel]):
    pages_count: int
    page_number: int
    results: list[ResponseModel]


@dataclass
class Paginator:
    page_number: int = Query(default=1, ge=1, alias="page[number]")
    page_size: int = Query(default=50, ge=1, alias="page[size]")

    def page(self, num_hits: int, items: list) -> PaginatedResponse:
        return PaginatedResponse(
            pages_count=max(1, self._pages_count(num_hits, self.page_size)),
            page_number=self.page_number,
            results=items,
        )

    def _pages_count(self, num_hits: int, page_size: int) -> int:
        return num_hits // page_size + (1 if num_hits % page_size else 0)
