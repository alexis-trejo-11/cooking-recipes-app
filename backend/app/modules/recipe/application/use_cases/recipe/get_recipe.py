import logging

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import GetRecipeUseCase
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import RecipeResponse
from app.modules.recipe.application.exceptions import RecipeNotFoundException

logger = logging.getLogger(__name__)


class GetRecipeUseCaseImpl(GetRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> RecipeResponse:
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        return RecipeResponse.from_recipe(recipe)
