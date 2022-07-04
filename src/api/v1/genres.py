from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.schemas import GenreSchema
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/", response_model=list[GenreSchema], summary="List Genres")
async def list_genres(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[GenreSchema]:
    """
    Get a list of genres.
    """
    genres = await genre_service.list()
    return [GenreSchema.from_model(genre) for genre in genres]


@router.get("/{genre_id}", response_model=GenreSchema, summary="Retrieve Genre")
async def retrieve_genre(
    genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)
) -> GenreSchema | None:
    """
    Retrieve a genre by id.
    """
    if genre := await genre_service.retrieve(genre_id):
        return GenreSchema.from_model(genre)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
