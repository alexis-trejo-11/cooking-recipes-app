import logging

from app.modules.recipe.domain.interfaces import RecipeReviewRepository
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.exceptions import (
    RecipeNotFoundException,
    ReviewDontFoundException,
)

from app.utils.core.pagination import PaginationParams
from ...dtos import ReviewResponse, ReviewPageResponse
from ..base import GetRecipeReviewsUseCase, GetUserReviewForRecipeUseCase

logger = logging.getLogger(__name__)


class GetRecipeReviewsUseCaseImpl(GetRecipeReviewsUseCase):
    def __init__(self, review_repository: RecipeReviewRepository) -> None:
        self.review_repository = review_repository

    async def execute(
        self, recipe_id: RecipeId, page_request: PaginationParams
    ) -> ReviewPageResponse:
        reviews_page = await self.review_repository.find_by_recipe_id(
            recipe_id, page_request
        )

        review_response_page = reviews_page.map(ReviewResponse.from_review)
        return ReviewPageResponse.from_page(review_response_page)


class GetUserReviewForRecipeUseCaseImpl(GetUserReviewForRecipeUseCase):
    def __init__(self, review_repository: RecipeReviewRepository):
        self.review_repository = review_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> ReviewResponse:
        review = await self.review_repository.find_by_recipe_id_and_user_id(
            recipe_id, user_id
        )
        if review is None:
            raise ReviewDontFoundException(recipe_id, user_id)

        return ReviewResponse.from_review(review)
