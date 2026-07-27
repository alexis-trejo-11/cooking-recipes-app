import logging
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.dtos import (
    RecipeSearchRequest,
    RecipePageResponse,
    RecipeSummaryResponse,
)
from app.modules.recipe.application.use_cases.base import SearchRecipesUseCase
from app.modules.recipe.infrastructure.persistence.specification_builder import (
    RecipeSearchCriteria,
    RecipeSpecificationBuilder,
    Specification,
)
from app.modules.recipe.application.exceptions import RecipeValidationException

logger = logging.getLogger(__name__)


class SearchRecipesUseCaseImpl(SearchRecipesUseCase):
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
            raise RecipeValidationException(
                "When including deleted recipes, at least one search criteria must be provided",
                "INVALID_SEARCH_CRITERIA",
            )

        if request.min_rating is not None and (
            request.min_rating < 0 or request.min_rating > 5
        ):
            raise RecipeValidationException(
                "Minimum rating must be between 0 and 5", "INVALID_RATING_RANGE"
            )

        if request.max_cooking_time is not None and request.max_cooking_time < 1:
            raise RecipeValidationException(
                "Maximum cooking time must be at least 1 minute", "INVALID_COOKING_TIME"
            )
