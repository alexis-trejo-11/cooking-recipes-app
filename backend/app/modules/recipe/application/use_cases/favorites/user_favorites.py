import logging

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import (
    GetUserFavoritesRecipesUseCase,
    GetRecipeFavoritesByUserUseCase,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.application.dtos import RecipeSummaryResponse
from app.utils.core.pagination import Page, PaginationParams

logger = logging.getLogger(__name__)


class GetUserFavoritesRecipesUseCaseImpl(GetUserFavoritesRecipesUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        favorite_recipes_page = await self.recipe_repository.find_favorites_by_user_id(
            user_id, page_request
        )
        return favorite_recipes_page.map(RecipeSummaryResponse.from_recipe)


class GetRecipeFavoritesByUserUseCaseImpl(GetRecipeFavoritesByUserUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        logger.debug(f"Fetching favorite recipes for user_id: {user_id}")

        recipe_page = await self.recipe_repository.find_favorites_by_user_id(
            user_id, page_request
        )
        return recipe_page.map(RecipeSummaryResponse.from_recipe)
