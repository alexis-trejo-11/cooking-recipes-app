from typing import TypeVar, Generic, Optional, Any, Dict, Callable
from math import ceil

TI = TypeVar("TI")  # Input type
TO = TypeVar("TO")  # Output type


class Page(Generic[TI]):
    """
    A generic paginated collection of items.

    This class provides a standardized way to represent paginated data
    with metadata about the pagination state.

    Type Parameters:
        T: The type of items in the collection

    Attributes:
        items (list[T]): The items for the current page
        total (int): Total number of items across all pages
        page (int): Current page number (1-indexed)
        size (int): Number of items per page
    """

    def __init__(self, items: list[TI], total: int = 0, page: int = 1, size: int = 10):
        """
        Initialize a Page instance.

        Args:
            items: List of items for the current page
            total: Total number of items across all pages. Defaults to 0.
            page: Current page number (1-indexed). Defaults to 1.
            size: Number of items per page. Defaults to 10.

        Raises:
            ValueError: If page or size are less than 1
        """
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")
        if size < 1:
            raise ValueError("Size must be greater than or equal to 1")

        self.items = items
        self.total = total
        self.page = page
        self.size = size

    @classmethod
    def empty(cls, page: int = 1, size: int = 10) -> "Page[TI]":
        """
        Create an empty page.

        Args:
            page: Page number. Defaults to 1.
            size: Page size. Defaults to 10.

        Returns:
            Page: An empty Page instance
        """
        return cls(items=[], total=0, page=page, size=size)

    @classmethod
    def from_total_list(
        cls, all_items: list[TI], page: int = 1, size: int = 10
    ) -> "Page[TI]":
        """
        Create a Page from a full list by slicing it.

        Args:
            all_items: Complete list of items to paginate
            page: Page number to extract. Defaults to 1.
            size: Number of items per page. Defaults to 10.

        Returns:
            Page: A Page instance with the sliced items
        """
        total = len(all_items)
        start = (page - 1) * size
        end = start + size
        items = all_items[start:end]

        return cls(items=items, total=total, page=page, size=size)

    def map(self, transform_fn: Callable[[TI], TO]) -> "Page[TO]":
        """
        Transform items using a mapping function while preserving pagination.

        Args:
            transform_fn: Function to transform each item from type TI to TO

        Returns:
            Page[TO]: New Page with transformed items

        Example:
            >>> page.map(RecipeSummaryResponse.from_recipe)
        """
        transformed_items = [transform_fn(item) for item in self.items]
        return Page(
            items=transformed_items,
            total=self.total,
            page=self.page,
            size=self.size,
        )

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get the limit for database queries (same as size)."""
        return self.size

    @property
    def total_pages(self) -> int:
        """Calculate the total number of pages."""
        if self.size == 0:
            return 0
        return ceil(self.total / self.size)

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1

    @property
    def next_page(self) -> Optional[int]:
        """Get the next page number, or None if no next page."""
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> Optional[int]:
        """Get the previous page number, or None if no previous page."""
        return self.page - 1 if self.has_prev else None

    @property
    def start_index(self) -> int:
        """Get the 1-based index of the first item on the current page."""
        if self.total == 0:
            return 0
        return self.offset + 1

    @property
    def end_index(self) -> int:
        """Get the 1-based index of the last item on the current page."""
        if self.total == 0:
            return 0
        return min(self.offset + self.size, self.total)

    def map_items(self, all_items: list[TI]) -> "Page[TI]":
        """
        Create a new Page with the same pagination metadata but different items.
        Args:
            all_items: New list of items for the current page
        Returns:
            Page: A new Page instance with updated items
        """
        return Page(
            items=all_items,
            total=self.total,
            page=self.page,
            size=self.size,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Page to a dictionary for serialization.

        Returns:
            dict: Dictionary representation of the page with all metadata
        """
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "size": self.size,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
            "next_page": self.next_page,
            "prev_page": self.prev_page,
            "start_index": self.start_index,
            "end_index": self.end_index,
        }

    def __repr__(self) -> str:
        return (
            f"Page(items={len(self.items)}, total={self.total}, "
            f"page={self.page}/{self.total_pages}, size={self.size})"
        )

    def __len__(self) -> int:
        """Return the number of items on the current page."""
        return len(self.items)

    def __iter__(self):
        """Allow iteration over the items."""
        return iter(self.items)


class PaginationParams:
    """
    A simple class to encapsulate pagination request parameters.
    """

    def __init__(
        self,
        page: int = 1,
        size: int = 10,
        sort_dir: Optional[str] = "asc",
        sort_by: Optional[str] = "created_at",
    ):
        """
        Initialize a PaginationParams instance.

        Args:
            page: The requested page number (1-indexed). Defaults to 1.
            size: The number of items per page. Defaults to 10.

        Raises:
            ValueError: If page or size are less than 1
        """
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")
        if size < 1:
            raise ValueError("Size must be greater than or equal to 1")
        if sort_dir not in ("asc", "desc"):
            raise ValueError("sort_dir must be either 'asc' or 'desc'")

        self.page = page
        self.size = size
        self.sort_dir = sort_dir
        self.sort_by = sort_by
