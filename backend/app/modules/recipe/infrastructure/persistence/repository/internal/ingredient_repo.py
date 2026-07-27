"""
Internal repository for ingredient management.

Handles ingredient operations as part of the recipe aggregate.
"""

from typing import List
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.domain.models.entities.recipe import Ingredient
from app.modules.recipe.infrastructure.persistence.models import IngredientModel
from ..base import BaseRepository


class IngredientRepository(BaseRepository):
    """Internal repository for ingredient management."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def delete_all(self, recipe_id: int) -> None:
        """Delete all ingredients for a recipe."""
        stmt = delete(IngredientModel).where(IngredientModel.recipe_id == recipe_id)
        await self.session.execute(stmt)

    async def create_all(self, recipe_id: int, ingredients: List[Ingredient]) -> None:
        """Bulk create ingredients for a recipe."""
        if not ingredients:
            return

        ingredient_models = [
            IngredientModel(
                recipe_id=recipe_id,
                name=ing.name,
                quantity_value=float(ing.quantity.value) if ing.quantity else 0.0,
                quantity_unit=ing.quantity.unit if ing.quantity else "units",
                is_optional=ing.is_optional,
                is_vegan=ing.properties.is_vegan,
                is_vegetarian=ing.properties.is_vegetarian,
                is_gluten_free=ing.properties.is_gluten_free,
                is_dairy_free=ing.properties.is_dairy_free,
                allergens=(
                    list(ing.properties.allergens) if ing.properties.allergens else []
                ),
                substitutes=ing.substitutes or [],
            )
            for ing in ingredients
        ]

        if ingredient_models:
            self.session.add_all(ingredient_models)
            await self.session.flush()
