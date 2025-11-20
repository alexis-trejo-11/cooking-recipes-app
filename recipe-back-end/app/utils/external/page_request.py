from pydantic import BaseModel, Field
from app.utils.core.pagination import PaginationParams
from typing import Optional


class PydanticPaginationResponse(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_next_page: bool
    has_prev_page: bool


class PydanticPaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (starting from 1)")
    size: int = Field(default=10, ge=1, le=100, description="Number of items per page")
    sort_dir: Optional[str] = Field(
        default="asc", description="Sort direction: 'asc' or 'desc'"
    )
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")

    def to_pagination_params(self) -> PaginationParams:
        return PaginationParams(
            page=self.page,
            size=self.size,
            sort_dir=self.sort_dir,
            sort_by=self.sort_by,
        )
