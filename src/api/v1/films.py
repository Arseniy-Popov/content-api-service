from enum import Enum
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.base import PaginatedResponse, paginate
from api.v1.schemas import FilmLongSchema, FilmShortSchema
from services.film import FilmService, get_film_service

router = APIRouter()


class SortFilmsOptions(str, Enum):
    RATING_DESC = "-imdb_rating"
    RATING_ASC = "imdb_rating"


@router.get(
    "/", response_model=PaginatedResponse[FilmShortSchema], summary="List Films"
)
async def list_films(
    sort: SortFilmsOptions = Query(default=SortFilmsOptions.RATING_DESC),
    genre: UUID | None = Query(default=None, alias="filter[genre]"),
    page_number: int = Query(default=1, ge=1, alias="page[number]"),
    page_size: int = Query(default=50, ge=1, alias="page[size]"),
    film_service: FilmService = Depends(get_film_service),
) -> PaginatedResponse[FilmShortSchema]:
    """
    Get a paginated list of films that sorted by rating and, optionally,
    filtered by genre.
    """
    films, num_hits = await film_service.search(
        None, sort, genre, page_number, page_size
    )
    films = [FilmShortSchema.from_model(film) for film in films]
    return paginate(num_hits, page_size, page_number, films)


@router.get(
    "/search", response_model=PaginatedResponse[FilmShortSchema], summary="Search Films"
)
async def search_films(
    query: str,
    page_number: int = Query(default=1, ge=1, alias="page[number]"),
    page_size: int = Query(default=50, ge=1, alias="page[size]"),
    film_service: FilmService = Depends(get_film_service),
) -> PaginatedResponse[FilmShortSchema]:
    """
    Get a paginated list of films that match the search query.

    Films are searched across the following attributes:
    - title (prioritized)
    - description
    - actors' names
    - writers' names
    - directors' names
    """
    films, num_hits = await film_service.search(
        query, None, None, page_number, page_size
    )
    films = [FilmShortSchema.from_model(film) for film in films]
    return paginate(num_hits, page_size, page_number, films)


@router.get("/{film_id}", response_model=FilmLongSchema, summary="Retrieve Film")
async def retrieve_film(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmLongSchema:
    """
    Retrieve a film by id.
    """
    film = await film_service.retrieve(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmLongSchema.from_model(film)
