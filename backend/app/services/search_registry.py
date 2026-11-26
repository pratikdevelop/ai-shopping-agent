"""In-memory registry for shopping search requests and their agent responses.

This is suitable for the initial single-process development server only.
Move searches and results to a persistent database before multi-worker deployment.
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

_SEARCHES: dict[UUID, SearchStatusResponse] = {}


def create_search(request: ProductSearchRequest) -> SearchStatusResponse:
    now = datetime.now(timezone.utc)
    record = SearchStatusResponse(
        search_id=uuid4(),
        status=SearchStatus.RUNNING,
        mode="langgraph",
        query=request.query,
        message="Your request has been sent to the LangGraph shopping agent.",
        warnings=[],
        answer=None,
        created_at=now,
        completed_at=None,
    )
    _SEARCHES[record.search_id] = record
    return record


def complete_search(
    search_id: UUID,
    answer: str,
    warnings: list[str] | None = None,
) -> SearchStatusResponse:
    previous = _SEARCHES[search_id]
    clean_warnings = warnings or []
    now = datetime.now(timezone.utc)
    record = previous.model_copy(
        update={
            "status": SearchStatus.PARTIAL if clean_warnings else SearchStatus.COMPLETED,
            "message": (
                "LangGraph returned a research response. Review the evidence warnings before relying on prices or offers."
                if clean_warnings
                else "LangGraph completed the shopping research request."
            ),
            "warnings": clean_warnings,
            "answer": answer,
            "completed_at": now,
        }
    )
    _SEARCHES[search_id] = record
    return record


def fail_search(search_id: UUID, safe_message: str) -> SearchStatusResponse:
    previous = _SEARCHES[search_id]
    now = datetime.now(timezone.utc)
    record = previous.model_copy(
        update={
            "status": SearchStatus.FAILED,
            "message": safe_message,
            "warnings": [safe_message],
            "answer": None,
            "completed_at": now,
        }
    )
    _SEARCHES[search_id] = record
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
        answer=record.answer,
        warnings=record.warnings,
    )
