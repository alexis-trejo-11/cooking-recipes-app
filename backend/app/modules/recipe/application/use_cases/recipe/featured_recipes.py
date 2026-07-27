import logging
from typing import List

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import GetFeaturedRecipesUseCase
from app.modules.recipe.application.dtos import RecipeSummaryResponse

logger = logging.getLogger(__name__)


class GetFeaturedRecipesUseCaseImpl(GetFeaturedRecipesUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self) -> List[RecipeSummaryResponse]:
        featured_recipes = await self.recipe_repository.find_featured_recipes(limit=3)
        return [
            RecipeSummaryResponse.from_recipe(recipe) for recipe in featured_recipes
        ]
