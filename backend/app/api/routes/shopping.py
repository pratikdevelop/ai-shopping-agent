"""Shopping search endpoints for the bootstrap API."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.shopping import (
    ProductSearchRequest,
    SearchDealsResponse,
    SearchStatusResponse,
)
from backend.app.services.search_registry import (
    create_placeholder_search,
    get_search,
    get_search_deals,
)

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.post(
    "/search",
    response_model=SearchStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and create a shopping search",
)
async def create_search(request: ProductSearchRequest) -> SearchStatusResponse:
    """Accept a search request and return a labelled placeholder result.

    The endpoint deliberately does not call the existing LangGraph agent yet.
    Agent integration is a later milestone, after the API contract is tested.
    """
    return create_placeholder_search(request)


@router.get(
    "/search/{search_id}",
    response_model=SearchStatusResponse,
    summary="Get shopping-search status",
)
async def read_search(search_id: UUID) -> SearchStatusResponse:
    record = get_search(search_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SEARCH_NOT_FOUND",
                "message": "No search with this ID exists in the current API process.",
            },
        )
    return record


@router.get(
    "/search/{search_id}/deals",
    response_model=SearchDealsResponse,
    summary="Get deals for a shopping search",
)
async def read_search_deals(search_id: UUID) -> SearchDealsResponse:
    deals = get_search_deals(search_id)
    if deals is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SEARCH_NOT_FOUND",
                "message": "No search with this ID exists in the current API process.",
            },
        )
    return deals
