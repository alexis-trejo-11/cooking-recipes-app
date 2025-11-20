import logging

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import UpdateRecipeUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import Recipe, RecipeId
from app.modules.recipe.domain.models.entities.recipe import (
    CuisineType,
    DifficultyLevel,
)
from app.modules.recipe.application.dtos import (
    UpdateRecipeRequest,
    RecipeUpdatedResponse,
)
from app.modules.recipe.application.exceptions import RecipeNotFoundException

logger = logging.getLogger(__name__)


class UpdateRecipeUseCaseImpl(UpdateRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, request: UpdateRecipeRequest, user_id: UserId
    ) -> RecipeUpdatedResponse:
        recipe = await self.recipe_repository.find_by_id_and_author(recipe_id, user_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        recipe.update_basic_info(
            name=request.name,
            description=request.description,
            cuisine=CuisineType(request.cuisine),
            difficulty=DifficultyLevel(request.difficulty),
        )

        self._update_recipe_details(recipe, request)

        recipe_updated = await self.recipe_repository.save(recipe)
        return RecipeUpdatedResponse(
            id=recipe_updated.id.value,
            name=recipe_updated.name,
            version=recipe_updated.version,
        )

    def _update_recipe_details(self, recipe: Recipe, request: UpdateRecipeRequest):
        serving_info = request.create_serving_info()
        cooking_time = request.create_cooking_time()
        nutritional_info = request.create_nutritional_info()
        steps = request.create_steps()
        ingredients = request.create_ingredients()
        tags = request.create_tags()
        meal_types = request.create_meal_types()

        if ingredients is not None:
            recipe.update_ingredients(ingredients)
        if steps is not None:
            recipe.update_steps(steps)
        if tags is not None:
            recipe.update_tags(tags)
        if meal_types is not None:
            recipe.update_meal_types(meal_types)
        if serving_info:
            recipe.update_serving_info(serving_info)
        if cooking_time:
            recipe.update_cooking_time(cooking_time)
        if nutritional_info:
            recipe.update_nutritional_info(nutritional_info)
