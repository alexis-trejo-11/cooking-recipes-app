import logging

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import IncrementViewCountUseCase
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.exceptions import RecipeNotFoundException

logger = logging.getLogger(__name__)


class IncrementViewCountUseCaseImpl(IncrementViewCountUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> None:
        logger.info(f"Incrementing view count for Recipe {recipe_id}")
        exists = await self.recipe_repository.exists_by_id(recipe_id)
        if not exists:
            raise RecipeNotFoundException(recipe_id)

        await self.recipe_repository.increase_view_count(recipe_id)
        logger.info(f"View count for Recipe {recipe_id} incremented successfully")
