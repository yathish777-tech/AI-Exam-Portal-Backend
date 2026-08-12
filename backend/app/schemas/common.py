"""
app/schemas/common.py
=====================
Shared Pydantic v2 schemas used across multiple modules.

- PaginationParams: validated query params for paginated list endpoints.
- PaginatedResponse: generic paginated response wrapper.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    PAGINATION_DEFAULT_PAGE,
    PAGINATION_DEFAULT_PAGE_SIZE,
    PAGINATION_MAX_PAGE_SIZE,
)

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Validated pagination query parameters."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(
        default=PAGINATION_DEFAULT_PAGE,
        ge=1,
        description="Page number (1-indexed).",
    )
    page_size: int = Field(
        default=PAGINATION_DEFAULT_PAGE_SIZE,
        ge=1,
        le=PAGINATION_MAX_PAGE_SIZE,
        description=f"Number of items per page. Max {PAGINATION_MAX_PAGE_SIZE}.",
    )

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET from page/page_size."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response."""

    model_config = ConfigDict(extra="forbid")

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class SuccessResponse(BaseModel):
    """Generic success response."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    message: str
