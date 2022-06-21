from typing import Generic, TypeVar

from pydantic.generics import GenericModel

ResponseModel = TypeVar("ResponseModel")


class PaginatedResponse(GenericModel, Generic[ResponseModel]):
    pages_count: int
    page_number: int
    results: list[ResponseModel]


def pages_count(num_hits: int, page_size: int) -> int:
    return num_hits // page_size + (1 if num_hits % page_size else 0)


def paginate(num_hits, page_size, page_number, items) -> PaginatedResponse:
    return PaginatedResponse(
        pages_count=pages_count(num_hits, page_size),
        page_number=page_number,
        results=items,
    )
