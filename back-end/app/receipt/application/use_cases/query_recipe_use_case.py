from typing import Optional
from app.utils.core.pagination import Page
from app.utils.page_request import PydnaticPageRequest
from app.auth.domain.interfaces import UserRepository
from app.auth.application.exceptions import UserNotFoundException
from app.auth.domain.user import UserId
from app.receipt.domain.interfaces import RecipeRepository
from app.receipt.domain.entities.recipe import Recipe, DietType, RecipeId
from .base import SearchRecipesUseCase, GetRecipeUseCase, GetUserRecipesUseCase
from ..dtos import (
    RecipeSearchRequest,
    RecipeSummaryResponse,
    RecipeResponse,
)


class GetRecipeUseCaseImpl(GetRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id_int: int) -> Optional[RecipeResponse]:
        recipe = await self.recipe_repository.get_by_id(RecipeId(recipe_id_int))
        if not recipe:
            return None

        return RecipeResponse.from_recipe(recipe)


class GetUserRecipesUseCaseImpl(GetUserRecipesUseCase):
    def __init__(
        self, recipe_repository: RecipeRepository, user_repository: UserRepository
    ):
        self.recipe_repository = recipe_repository
        self.user_repository = user_repository

    async def execute(
        self, author_id_int: int, page_request: PydnaticPageRequest
    ) -> Page[RecipeSummaryResponse]:
        author_id = UserId(author_id_int)
        user = await self.user_repository.get_by_id(author_id)
        if not user:
            raise UserNotFoundException(f"User with ID {author_id} not found")

        recipe_page = await self.recipe_repository.get_by_author(
            author_id, page_request.to_request()
        )

        return recipe_page.map(RecipeSummaryResponse.from_recipe)


class SearchRecipeUseCaseImpl(SearchRecipesUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, request: RecipeSearchRequest
    ) -> Page[RecipeSummaryResponse]:
        recipe_page = await self.recipe_repository.search(
            name=request.query,
            page_request=request.pagination.to_request(),
        )
        return recipe_page.map(RecipeSummaryResponse.from_recipe)

    def _matches_filters(self, recipe: Recipe, request: RecipeSearchRequest) -> bool:
        # Filter by difficulty
        if request.difficulty and recipe.difficulty != request.difficulty:
            return False

        # Filter by cuisine
        if request.cuisine and recipe.cuisine != request.cuisine:
            return False

        # Filter by meal type
        if request.meal_type and request.meal_type not in recipe.get_meal_types():
            return False

        # Filter by diet
        if request.diet and not recipe.is_suitable_for_diet(DietType(request.diet)):
            return False

        # Filter by preparation and cooking time
        cooking_time = recipe.get_cooking_time()
        if (
            request.max_prep_time
            and cooking_time
            and cooking_time.prep_minutes > request.max_prep_time
        ):
            return False

        if (
            request.max_cook_time
            and cooking_time
            and cooking_time.cook_minutes > request.max_cook_time
        ):
            return False

        # Filter by minimum rating
        if request.min_rating:
            avg_rating = recipe.get_average_rating()
            if not avg_rating or avg_rating < request.min_rating:
                return False

        # Filter by tags
        if request.tags:
            recipe_tag_names = {tag.name for tag in recipe.get_tags()}
            if not all(tag in recipe_tag_names for tag in request.tags):
                return False

        # Exclude allergens
        if request.exclude_allergens:
            recipe_allergens = recipe.get_allergens()
            if any(
                allergen in recipe_allergens for allergen in request.exclude_allergens
            ):
                return False

        return True
