from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.base import PaginatedResponse, paginate
from api.v1.schemas import PersonSchema, PersonsFilmsSchema
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/search", response_model=PaginatedResponse[PersonSchema])
async def search_person(
    query: str,
    page_number: int = Query(default=1, ge=1, alias="page[number]"),
    page_size: int = Query(default=50, ge=1, alias="page[size]"),
    person_service: PersonService = Depends(get_person_service),
) -> PaginatedResponse[PersonSchema]:
    persons, num_hits = await person_service.search(query, page_number, page_size)
    persons = [PersonSchema.from_model(person) for person in persons]
    return paginate(num_hits, page_size, page_number, persons)


@router.get("/{person_id}", response_model=PersonSchema)
async def retrieve_person(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonSchema:
    if person := await person_service.retrieve(person_id):
        return PersonSchema.from_model(person)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{person_id}/films", response_model=PersonsFilmsSchema)
async def list_persons_films(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonsFilmsSchema:
    if persons_films := await person_service.list_movies(person_id):
        return PersonsFilmsSchema.from_model(persons_films)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
