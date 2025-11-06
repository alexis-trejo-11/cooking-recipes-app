from pydantic import BaseModel, Field
from app.utils.core.pagination import PageRequest


class PydnaticPageRequest(BaseModel):
    page: int = Field(1, ge=1, description="Page number (starting from 1)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    order_by: str = Field("default", description="Field to order by")
    sort_direction: str = Field("asc", description="Sort direction: 'asc' or 'desc'")

    def to_request(self) -> PageRequest:
        return PageRequest(
            page=self.page,
            size=self.page_size,
            sort_by=self.order_by,
            sort_dir=self.sort_direction,
        )
