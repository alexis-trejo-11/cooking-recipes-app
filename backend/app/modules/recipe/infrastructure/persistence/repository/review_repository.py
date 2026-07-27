"""
SQLAlchemy implementation of RecipeReviewRepository.

Handles recipe review operations including creating, updating,
and deleting reviews.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Any
from unittest import result
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ......utils.core.pagination import Page, PaginationParams
from app.modules.recipe.domain.interfaces import RecipeReviewRepository
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.domain.models.entities.review import Review
from app.modules.recipe.infrastructure.persistence.models import ReviewModel
from .base import BaseRepository, QueryBuilderMixin

logger = logging.getLogger(__name__)


class SqlAlchemyRecipeReviewRepository(
    RecipeReviewRepository, BaseRepository, QueryBuilderMixin
):
    """
    Repository for recipe review operations.

    Handles the many-to-many relationship between users and recipe reviews
    with ratings and comments.
    """

    def __init__(self, session: AsyncSession):
        BaseRepository.__init__(self, session)

    async def find_by_recipe_id(
        self, recipe_id: RecipeId, page_request: PaginationParams
    ) -> Page[Review]:
        query = select(ReviewModel).where(ReviewModel.recipe_id == recipe_id.value)

        total = await self._count_results(query)

        query = self._apply_sorting(query, page_request)
        query = self._apply_pagination(query, page_request)

        result = await self.session.execute(query)
        review_models = result.scalars().all()
        reviews = [self._to_domain(rm) for rm in review_models]

        return Page(
            items=reviews, total=total, page=page_request.page, size=page_request.size
        )

    async def find_by_recipe_id_and_user_id(
        self, recipe_id: RecipeId, user_id: UserId
    ) -> Review | None:
        stmt = select(ReviewModel).where(
            and_(
                ReviewModel.recipe_id == recipe_id.value,
                ReviewModel.user_id == user_id.value,
            )
        )
        result = await self.session.execute(stmt)
        review_model = result.scalar_one_or_none()

        return self._to_domain(review_model) if review_model else None

    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Check if review exists for recipe by user.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Returns:
            True if review exists, False otherwise
        """
        stmt = select(
            select(ReviewModel.recipe_id)
            .where(
                and_(
                    ReviewModel.recipe_id == recipe_id.value,
                    ReviewModel.user_id == user_id.value,
                )
            )
            .exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def count_by_recipe(self, recipe_id: int) -> int:
        """
        Count reviews for a recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Number of reviews for the recipe
        """
        stmt = (
            select(func.count())
            .select_from(ReviewModel)
            .where(ReviewModel.recipe_id == recipe_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def save(self, review: Review) -> None:
        """
        Create or update a review.

        Args:
            review: Review entity to save

        Raises:
            Exception: If save operation fails
        """
        logger.debug(
            f"Saving review for recipe {review.recipe_id} by user {review.user_id}"
        )

        try:
            existing_review = await self._find_by_recipe_and_user(
                review.recipe_id.value, review.user_id.value
            )

            if existing_review:
                await self._update(
                    existing_review.recipe_id,
                    existing_review.user_id,
                    review.rating,
                    review.comment,
                )
                logger.debug(f"Updated existing review")
            else:
                await self._create(
                    review.recipe_id.value,
                    review.user_id.value,
                    review.rating,
                    review.comment,
                )
                logger.debug(f"Created new review")

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving review: {e}", exc_info=True)
            raise

    async def delete(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """
        Delete a review.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Raises:
            Exception: If delete operation fails
        """
        logger.debug(f"Deleting review for recipe {recipe_id} by user {user_id}")

        try:
            stmt = delete(ReviewModel).where(
                and_(
                    ReviewModel.recipe_id == recipe_id.value,
                    ReviewModel.user_id == user_id.value,
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.debug(f"Successfully deleted review")

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting review: {e}", exc_info=True)
            raise

    async def _find_by_recipe_and_user(
        self, recipe_id: int, user_id: int
    ) -> Optional[Any]:
        """Find existing review by recipe and user."""
        stmt = select(ReviewModel).where(
            and_(
                ReviewModel.recipe_id == recipe_id,
                ReviewModel.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.first()

    async def _create(
        self, recipe_id: int, user_id: int, rating: int, comment: Optional[str]
    ) -> None:
        """Create new review."""
        review_model = ReviewModel(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(review_model)

    async def _update(
        self, recipe_id: int, user_id: int, rating: int, comment: Optional[str]
    ) -> None:
        """Update existing review."""
        stmt = (
            update(ReviewModel)
            .where(
                and_(
                    ReviewModel.recipe_id == recipe_id,
                    ReviewModel.user_id == user_id,
                )
            )
            .values(
                rating=rating,
                comment=comment,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

    def _to_domain(self, review_model: Any) -> Review:
        return Review(
            recipe_id=RecipeId(review_model.recipe_id),
            user_id=UserId(review_model.user_id),
            rating=review_model.rating,
            comment=review_model.comment if review_model.comment else "",
            created_at=review_model.created_at,
            updated_at=review_model.updated_at,
        )

    def _get_sort_column(self, sort_by: str) -> Any:
        """Get SQLAlchemy column for review sorting."""

        sort_columns = {
            "created_at": ReviewModel.created_at,
            "updated_at": ReviewModel.updated_at,
            "rating": ReviewModel.rating,
        }
        return sort_columns.get(sort_by, ReviewModel.created_at)
