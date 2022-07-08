from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.base import PaginatedResponse, Paginator
from api.v1.schemas import PersonSchema, PersonsFilmsSchema
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search", response_model=PaginatedResponse[PersonSchema], summary="Search Persons"
)
async def search_persons(
    query: str,
    paginator: Paginator = Depends(Paginator),
    person_service: PersonService = Depends(get_person_service),
) -> PaginatedResponse[PersonSchema]:
    """
    Get a paginated list of persons that match the search query.

    The search is conducted only on the full name attribute.
    """
    persons, num_hits = await person_service.search(
        query, paginator.page_number, paginator.page_size
    )
    persons = [PersonSchema.from_model(person) for person in persons]
    return paginator.page(num_hits, persons)


@router.get("/{person_id}", response_model=PersonSchema, summary="Retrieve Person")
async def retrieve_person(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonSchema:
    """
    Retrieve a person by id.
    """
    if person := await person_service.retrieve(person_id):
        return PersonSchema.from_model(person)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get(
    "/{person_id}/films",
    response_model=PersonsFilmsSchema,
    summary="List Person's Films",
)
async def list_persons_films(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonsFilmsSchema:
    """
    List films a person is associated with.
    """
    if persons_films := await person_service.list_movies(person_id):
        return PersonsFilmsSchema.from_model(persons_films)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
