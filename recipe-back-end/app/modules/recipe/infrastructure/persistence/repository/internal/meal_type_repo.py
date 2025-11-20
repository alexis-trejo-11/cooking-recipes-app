# app/modules/recipe/infrastructure/persistence/repositories/internal/meal_type_repo.py
"""
Internal repository for meal type management.

Handles meal type operations as part of the recipe aggregate,
including creating, deleting, and listing meal types.
"""

import logging
from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.domain.models.entities.recipe import MealType
from app.modules.recipe.infrastructure.persistence.models import RecipeMealTypeModel
from ..base import BaseRepository

logger = logging.getLogger(__name__)


class MealTypeRepository(BaseRepository):
    """
    Internal repository for meal type management.

    Handles the many-to-many relationship between recipes and meal types.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_all(self) -> List[MealType]:
        """
        List all distinct meal types used in recipes.

        Returns:
            List of unique meal types across all recipes
        """
        logger.debug("Retrieving all distinct meal types")

        stmt = select(RecipeMealTypeModel.meal_type).distinct()
        result = await self.session.execute(stmt)
        meal_type_rows = result.scalars().all()

        meal_types = [MealType(mt) for mt in meal_type_rows]
        logger.debug(f"Found {len(meal_types)} distinct meal types")

        return meal_types

    async def delete_all(self, recipe_id: int) -> None:
        """
        Delete all meal types for a specific recipe.

        Args:
            recipe_id: ID of the recipe to clear meal types for

        Note:
            This is typically used during recipe updates to remove old relationships
        """
        logger.debug(f"Deleting all meal types for recipe {recipe_id}")

        stmt = delete(RecipeMealTypeModel).where(
            RecipeMealTypeModel.recipe_id == recipe_id
        )
        await self.session.execute(stmt)
        logger.debug(f"Successfully deleted meal types for recipe {recipe_id}")

    async def create_all(self, recipe_id: int, meal_types: List[MealType]) -> None:
        """
        Bulk create meal types for a recipe.

        Args:
            recipe_id: ID of the recipe to associate meal types with
            meal_types: List of meal types to associate

        Note:
            If meal_types is empty, no operation is performed
        """
        if not meal_types:
            logger.debug(f"No meal types to create for recipe {recipe_id}")
            return

        logger.debug(f"Creating {len(meal_types)} meal types for recipe {recipe_id}")

        meal_type_models = [
            RecipeMealTypeModel(
                recipe_id=recipe_id,
                meal_type=mt.value if isinstance(mt, MealType) else mt,
            )
            for mt in meal_types
        ]

        if meal_type_models:
            self.session.add_all(meal_type_models)
            await self.session.flush()
            logger.debug(
                f"Successfully created {len(meal_type_models)} meal type associations"
            )
