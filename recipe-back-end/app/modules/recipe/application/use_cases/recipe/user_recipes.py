import logging

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import GetUserRecipesUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.application.dtos import (
    RecipePageResponse,
    RecipeSummaryResponse,
)
from app.utils.external.page_request import PydanticPaginationParams
from app.modules.recipe.infrastructure.persistence.specification_builder import (
    RecipeSearchCriteria,
    RecipeSpecificationBuilder,
)
from app.modules.recipe.application.exceptions import RecipeValidationException

logger = logging.getLogger(__name__)


class GetUserRecipesUseCaseImpl(GetUserRecipesUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, author_id: UserId, page_params: PydanticPaginationParams
    ) -> RecipePageResponse:
        if author_id.is_zero():
            raise RecipeValidationException(
                "Author ID must be a positive integer", "INVALID_AUTHOR_ID"
            )

        specification = RecipeSpecificationBuilder.build_from_criteria(
            RecipeSearchCriteria(author_id=author_id)
        )

        recipe_page = await self.recipe_repository.search(
            spec=specification,
            page_request=page_params.to_pagination_params(),
        )

        response_page = recipe_page.map(RecipeSummaryResponse.from_recipe)
        return RecipePageResponse.from_page(response_page)
