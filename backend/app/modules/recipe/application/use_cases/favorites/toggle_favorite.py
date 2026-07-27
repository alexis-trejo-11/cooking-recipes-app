import logging

from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeFavoriteRepository,
)
from app.modules.recipe.application.use_cases.base import (
    ToggleFavoriteUseCase,
    IsFavoriteUseCase,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.exceptions import RecipeNotFoundException

logger = logging.getLogger(__name__)


class ToggleFavoriteUseCaseImpl(ToggleFavoriteUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        recipe_favorite_repository: RecipeFavoriteRepository,
    ) -> None:
        self.recipe_repository = recipe_repository
        self.recipe_favorite_repository = recipe_favorite_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        logger.info(
            f"Toggling favorite for recipe_id: {recipe_id} by user_id: {user_id}"
        )

        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        await self.recipe_favorite_repository.toggle(recipe_id, user_id)
        logger.info(f"Recipe {recipe_id} favorite status toggled for user {user_id}")


class IsFavoriteUseCaseImpl(IsFavoriteUseCase):
    def __init__(self, recipe_favorite_repository: RecipeFavoriteRepository) -> None:
        self.recipe_favorite_repository = recipe_favorite_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        logger.info(f"Checking if Recipe {recipe_id} is favorite for User {user_id}")
        is_favorite = await self.recipe_favorite_repository.exists(recipe_id, user_id)
        logger.info(
            f"Recipe {recipe_id} is {'a' if is_favorite else 'not a'} favorite for User {user_id}"
        )
        return is_favorite
