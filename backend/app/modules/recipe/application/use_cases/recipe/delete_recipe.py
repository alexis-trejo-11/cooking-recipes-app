import logging
from typing import Optional

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import (
    DeleteRecipeUseCase,
    RestoreRecipeUseCase,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.exceptions import RecipeNotFoundException
from app.modules.recipe.domain.models.entities.recipe import Recipe

logger = logging.getLogger(__name__)


class DeleteRecipeUseCaseImpl(DeleteRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId, author_id: Optional[UserId]) -> None:
        logger.info(f"Executing DeleteRecipeUseCase for recipe_id: {recipe_id}")

        recipe = await self._get_recipe_or_raise(recipe_id, author_id)
        recipe.soft_delete()

        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe soft deleted: {recipe.id}")

    async def _get_recipe_or_raise(
        self, recipe_id: RecipeId, author_id: Optional[UserId]
    ) -> "Recipe":
        if author_id:
            logger.info(f"Author ID provided: {author_id}")
            recipe = await self.recipe_repository.find_by_id_and_author(
                recipe_id, author_id
            )
        else:
            logger.info("No Author ID provided")
            recipe = await self.recipe_repository.find_by_id(recipe_id)

        if not recipe:
            raise RecipeNotFoundException(recipe_id)
        logger.info(f"Recipe found for delete: {recipe.id}")

        return recipe


class RestoreRecipeUseCaseImpl(RestoreRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> None:
        logger.info(f"Executing RestoreRecipeUseCase for recipe_id: {recipe_id}")

        recipe = await self.recipe_repository.find_by_id(
            include_deleted=True, recipe_id=recipe_id
        )
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        recipe.restore()
        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe {recipe_id} restored")
