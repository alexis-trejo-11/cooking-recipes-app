import logging
from decimal import Decimal

from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeReviewRepository,
)
from app.modules.recipe.application.use_cases.base import CreateReviewUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import (
    CreateReviewRequest,
    ReviewCreatedResponse,
)
from app.modules.recipe.application.exceptions import (
    RecipeNotFoundException,
    RecipeValidationException,
)

logger = logging.getLogger(__name__)


class CreateReviewUseCaseImpl(CreateReviewUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        review_repository: RecipeReviewRepository,
    ):
        self.recipe_repository = recipe_repository
        self.review_repository = review_repository

    async def execute(
        self, request: CreateReviewRequest, user_id: UserId, recipe_id: RecipeId
    ) -> ReviewCreatedResponse:
        logger.info(f"User {user_id} is adding review to Recipe {recipe_id}")
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        if recipe.author_id == user_id:
            raise RecipeValidationException(
                f"User {user_id} cannot review their own Recipe {recipe_id}",
                "SELF_REVIEW_NOT_ALLOWED",
            )

        existing_review = await self.review_repository.exists(recipe_id, user_id)
        if existing_review:
            raise RecipeValidationException(
                f"User {user_id} has already reviewed Recipe {recipe_id}",
                "DUPLICATE_REVIEW",
            )

        review = request.to_domain(recipe_id, user_id)
        await self.review_repository.save(review)

        logger.info(f"User {user_id} review saved for Recipe {  recipe_id}")
        return ReviewCreatedResponse(
            recipe_id=review.recipe_id.value,
            new_average_rating=Decimal(
                str(recipe.average_rating) if recipe.average_rating else "0"
            ),
            total_ratings=recipe.review_count,
        )
