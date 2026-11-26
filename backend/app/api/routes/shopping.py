"""Shopping-search endpoints backed by the existing LangGraph agent."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from backend.app.schemas.shopping import (
    ProductSearchRequest,
    SearchDealsResponse,
    SearchStatusResponse,
)
from backend.app.services.agent_service import ShoppingAgentError, run_shopping_research
from backend.app.services.search_registry import (
    complete_search,
    create_search,
    fail_search,
    get_search,
    get_search_deals,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.post(
    "/search",
    response_model=SearchStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Run a shopping search with LangGraph",
)
async def create_search_endpoint(
    payload: ProductSearchRequest,
    request: Request,
) -> SearchStatusResponse:
    """Run the shopping agent and return its final answer and evidence warnings.

    This first integration is synchronous from the API client's perspective:
    the response is returned when LangGraph finishes. Background jobs and
    polling can be added later for long-running searches.
    """
    record = create_search(payload)

    try:
        answer, warnings = await run_shopping_research(payload, request.app)
        return complete_search(record.search_id, answer, warnings)
    except ShoppingAgentError as exc:
        logger.warning("Shopping search %s failed: %s", record.search_id, exc)
        return fail_search(
            record.search_id,
            "Shopping research failed. Check the backend logs and verify your LLM provider and Fleet MCP configuration.",
        )
    except Exception:
        logger.exception("Unexpected error during shopping search %s", record.search_id)
        return fail_search(
            record.search_id,
            "An unexpected error interrupted shopping research. Check the backend logs.",
        )


@router.get(
    "/search/{search_id}",
    response_model=SearchStatusResponse,
    summary="Get shopping-search status and answer",
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
    summary="Get the research answer and structured deals for a search",
)
async def read_search_deals(search_id: UUID) -> SearchDealsResponse:
    result = get_search_deals(search_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SEARCH_NOT_FOUND",
                "message": "No search with this ID exists in the current API process.",
            },
        )
    return result
