"""
Base repository classes and common utilities for SQLAlchemy implementations.
"""

from typing import Any, List
from sqlalchemy import Select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.core.pagination import PaginationParams
from app.modules.recipe.infrastructure.persistence.models import RecipeModel


class BaseRepository:
    """Base class with common repository functionality."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_sorting(self, query: Select, page_request: PaginationParams) -> Select:
        """
        Apply sorting to SQLAlchemy query.

        Args:
            query: SQLAlchemy select query
            page_request: Pagination parameters with sorting info

        Returns:
            Query with sorting applied
        """
        sort_column = self._get_sort_column(page_request.sort_by or "created_at")

        if page_request.sort_dir == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        return query.order_by(sort_column)

    def _apply_pagination(
        self, query: Select, page_request: PaginationParams
    ) -> Select:
        """
        Apply pagination to SQLAlchemy query.

        Args:
            query: SQLAlchemy select query
            page_request: Pagination parameters

        Returns:
            Query with pagination applied
        """
        offset = (page_request.page - 1) * page_request.size
        return query.offset(offset).limit(page_request.size)

    def _get_sort_column(self, sort_by: str) -> Any:
        """
        Get SQLAlchemy column for sorting.

        Args:
            sort_by: Field name to sort by

        Returns:
            SQLAlchemy column for sorting
        """
        sort_columns = {
            "created_at": RecipeModel.created_at,
            "updated_at": RecipeModel.updated_at,
            "name": RecipeModel.name,
            "views": RecipeModel.view_count,
        }
        return sort_columns.get(sort_by, RecipeModel.created_at)


class QueryBuilderMixin:
    """Mixin for building complex queries with relationships."""

    # This mixin requires a session attribute to be available
    session: AsyncSession

    def _apply_relationship_loading(self, query: Select) -> Select:
        """
        Apply eager loading for recipe relationships.

        Args:
            query: SQLAlchemy select query

        Returns:
            Query with relationship loading applied
        """
        from sqlalchemy.orm import selectinload
        from app.modules.recipe.infrastructure.persistence.models import RecipeModel

        return query.options(
            selectinload(RecipeModel.ingredients),
            selectinload(RecipeModel.steps),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.meal_types),
        )

    def _should_apply_join(self, join: Any) -> bool:
        """
        Check if join should be applied (filter out relationships).

        Args:
            join: SQLAlchemy join condition

        Returns:
            True if join should be applied
        """
        from app.modules.recipe.infrastructure.persistence.models import RecipeModel

        relationship_attrs = [
            RecipeModel.ingredients,
            RecipeModel.steps,
            RecipeModel.tags,
            RecipeModel.meal_types,
        ]
        return join not in relationship_attrs

    async def _count_results(self, query: Select) -> int:
        """
        Count total results for a query.

        Args:
            query: SQLAlchemy select query

        Returns:
            Total count of results
        """
        count_query = query.with_only_columns(func.count()).order_by(None)
        result = await self.session.execute(count_query)
        return result.scalar() or 0
