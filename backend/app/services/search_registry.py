"""Temporary in-memory search registry for the API bootstrap phase.

This registry is intentionally non-persistent. It will be replaced by the
LangGraph search service and a durable repository in later implementation
phases. Do not use it for production workloads.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from backend.app.schemas.shopping import (
    ProductSearchRequest,
    SearchDealsResponse,
    SearchStatus,
    SearchStatusResponse,
)

PLACEHOLDER_WARNING = (
    "Shopping research is not connected yet. This is a placeholder API response; "
    "no retailer prices, offers, stock, or showroom availability have been checked."
)

_SEARCHES: dict[UUID, SearchStatusResponse] = {}


def create_placeholder_search(request: ProductSearchRequest) -> SearchStatusResponse:
    """Create a clearly labelled placeholder record without calling an agent."""
    now = datetime.now(timezone.utc)
    record = SearchStatusResponse(
        search_id=uuid4(),
        status=SearchStatus.COMPLETED,
        mode="placeholder",
        query=request.query,
        message="Request validated. Live shopping research is not connected yet.",
        warnings=[PLACEHOLDER_WARNING],
        created_at=now,
        completed_at=now,
    )
    _SEARCHES[record.search_id] = record
    return record


def get_search(search_id: UUID) -> SearchStatusResponse | None:
    return _SEARCHES.get(search_id)


def get_search_deals(search_id: UUID) -> SearchDealsResponse | None:
    record = _SEARCHES.get(search_id)
    if record is None:
        return None

    return SearchDealsResponse(
        search_id=record.search_id,
        status=record.status,
        mode=record.mode,
        deals=[],
        warnings=record.warnings,
    )
    