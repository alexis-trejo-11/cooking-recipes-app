from ...domain.entities.recipe import RecipeId
from ....auth.domain.user import UserId
from ..dtos import RecipeUpdatedResponse, UpdateRecipeRequest
from .base import UpdateRecipeUseCase
from app.receipt.domain.interfaces import RecipeRepository
from ..exceptions import RecipeNotFoundException

class UpdateRecipeUseCaseImpl(UpdateRecipeUseCase):
  def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, request: UpdateRecipeRequest, user_id: UserId
    ) -> RecipeUpdatedResponse:
        recipe = await self.recipe_repository.find_by_id_and_author(recipe_id, user_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.update_basic_info(
            name=request.name,
            description=request.description,
            cuisine=request.cuisine,
            difficulty=request.difficulty
        )
