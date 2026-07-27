# app/modules/recipe/infrastructure/persistence/repositories/favorite_repository.py
"""
SQLAlchemy implementation of RecipeFavoriteRepository.

Handles recipe favorite operations including toggling favorites
and checking favorite status.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import func, select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.domain.interfaces import RecipeFavoriteRepository
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.infrastructure.persistence.models import recipe_favorites
from .base import BaseRepository

logger = logging.getLogger(__name__)


class SqlAlchemyRecipeFavoriteRepository(RecipeFavoriteRepository, BaseRepository):
    """
    Repository for recipe favorite operations.

    Handles the many-to-many relationship between users and favorite recipes.
    """

    def __init__(self, session: AsyncSession):
        BaseRepository.__init__(self, session)

    async def count_by_recipe(self, recipe_id: int) -> int:
        """
        Count favorites for a recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Number of favorites for the recipe
        """
        stmt = (
            select(func.count())
            .select_from(recipe_favorites)
            .where(recipe_favorites.c.recipe_id == recipe_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def toggle(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Toggle favorite status for a recipe.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Returns:
            True if favorite was added, False if removed
        """
        logger.debug(f"Toggling favorite for recipe {recipe_id} by user {user_id}")

        is_favorite = await self.exists(recipe_id, user_id)

        if is_favorite:
            await self._remove(recipe_id, user_id)
            logger.debug(f"Removed favorite for recipe {recipe_id} by user {user_id}")
            return False
        else:
            await self._add(recipe_id, user_id)
            logger.debug(f"Added favorite for recipe {recipe_id} by user {user_id}")
            return True

    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Check if recipe is favorited by user.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Returns:
            True if recipe is favorited, False otherwise
        """
        stmt = select(
            select(recipe_favorites.c.recipe_id)
            .where(
                and_(
                    recipe_favorites.c.recipe_id == recipe_id.value,
                    recipe_favorites.c.user_id == user_id.value,
                )
            )
            .exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def _add(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Add recipe to user's favorites."""
        stmt = recipe_favorites.insert().values(
            recipe_id=recipe_id.value,
            user_id=user_id.value,
            favorited_at=datetime.now(timezone.utc),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def _remove(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Remove recipe from user's favorites."""
        stmt = delete(recipe_favorites).where(
            and_(
                recipe_favorites.c.recipe_id == recipe_id.value,
                recipe_favorites.c.user_id == user_id.value,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
