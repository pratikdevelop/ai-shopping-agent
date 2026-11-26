"""Pydantic schemas for shopping search requests and responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SearchStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProductSearchRequest(BaseModel):
    """A validated product-research request from the frontend."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(min_length=3, max_length=1000)
    budget_amount: Decimal | None = Field(default=None, gt=Decimal("0"))
    currency: str = Field(default="INR", min_length=3, max_length=3)
    country: str = Field(default="India", min_length=2, max_length=80)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    brand: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    condition: str = Field(default="new", max_length=40)
    specifications: dict[str, Any] = Field(default_factory=dict)
    preferred_retailers: list[str] = Field(default_factory=list, max_length=15)
    include_local_stores: bool = False

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_local_search_location(self) -> "ProductSearchRequest":
        if self.include_local_stores and not any((self.city, self.state, self.postal_code)):
            raise ValueError(
                "Provide a city, state, or postal code when local-store search is enabled."
            )
        return self


class SearchStatusResponse(BaseModel):
    search_id: UUID
    status: SearchStatus
    mode: str = "langgraph"
    query: str
    message: str
    warnings: list[str] = Field(default_factory=list)
    answer: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class SearchDealsResponse(BaseModel):
    search_id: UUID
    status: SearchStatus
    mode: str = "langgraph"
    deals: list[dict[str, Any]] = Field(default_factory=list)
    answer: str | None = None
    warnings: list[str] = Field(default_factory=list)
