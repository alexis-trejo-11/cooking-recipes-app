from app.utils.core.pagination import Page
from app.utils.external.page_request import PydanticPaginationParams
from app.modules.recipe.application.exceptions import RecipeNotFoundException
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.infrastructure.persistence.specification_builder import (
    RecipeSearchCriteria,
    RecipeSpecificationBuilder,
    Specification,
)
from .base import SearchRecipesUseCase, GetRecipeUseCase, GetUserRecipesUseCase
from ..dtos import (
    RecipeSearchRequest,
    RecipeSummaryResponse,
    RecipeResponse,
    RecipePageResponse,
)


class GetRecipeUseCaseImpl(GetRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id_int: int) -> RecipeResponse:
        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id_int))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id_int} not found")

        return RecipeResponse.from_recipe(recipe)


class GetUserRecipesUseCaseImpl(GetUserRecipesUseCase):
    """Implementation of get user recipes use case."""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, author_id: UserId, page_params: PydanticPaginationParams
    ) -> RecipePageResponse:
        if author_id.is_zero():
            raise ValueError("Author ID must be a positive integer")

        specification = RecipeSpecificationBuilder.build_from_criteria(
            RecipeSearchCriteria(author_id=author_id)
        )

        recipe_page = await self.recipe_repository.search(
            spec=specification,
            page_request=page_params.to_pagination_params(),
        )

        response_page = recipe_page.map(RecipeSummaryResponse.from_recipe)
        return RecipePageResponse.from_page(response_page)


class SearchRecipesUseCaseImpl(SearchRecipesUseCase):
    """Implementation of search recipes use case."""

    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, request: RecipeSearchRequest) -> RecipePageResponse:
        self._validate_search_request(request)

        search_criteria = request.to_search_criteria()
        specification = RecipeSpecificationBuilder().build_from_criteria(
            search_criteria
        )

        if specification is None:
            specification = self._get_default_specification()

        recipe_page = await self.recipe_repository.search(
            spec=specification, page_request=request.pagination.to_pagination_params()
        )

        response_page = recipe_page.map(RecipeSummaryResponse.from_recipe)
        return RecipePageResponse.from_page(response_page)

    def _get_default_specification(self) -> Specification:
        only_active_search_criteria = RecipeSearchCriteria(include_deleted=False)
        return RecipeSpecificationBuilder().build_from_criteria(
            only_active_search_criteria
        )

    def _validate_search_request(self, request: RecipeSearchRequest) -> None:
        """Validate search request parameters."""
        # Check if at least one search criteria is provided when including deleted recipes
        if request.include_deleted and not any(
            [
                request.name,
                request.author_id,
                request.difficulty,
                request.cuisine,
                request.tags,
                request.meal_types,
                request.ingredient_name,
                request.min_rating,
                request.max_cooking_time,
            ]
        ):
            raise ValueError(
                "When including deleted recipes, at least one search criteria must be provided"
            )

        if request.min_rating is not None and (
            request.min_rating < 0 or request.min_rating > 5
        ):
            raise ValueError("Minimum rating must be between 0 and 5")

        if request.max_cooking_time is not None and request.max_cooking_time < 1:
            raise ValueError("Maximum cooking time must be at least 1 minute")
