import logging
from decimal import Decimal

from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeReviewRepository,
)
from app.modules.recipe.application.use_cases.base import UpdateReviewUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import UpdateReviewRequest
from app.modules.recipe.application.exceptions import (
    RecipeNotFoundException,
    RecipeValidationException,
)

logger = logging.getLogger(__name__)


class UpdateReviewUseCaseImpl(UpdateReviewUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        review_repository: RecipeReviewRepository,
    ):
        self.recipe_repository = recipe_repository
        self.review_repository = review_repository

    async def execute(
        self,
        user_id: UserId,
        recipe_id: RecipeId,
        update_data: UpdateReviewRequest,
    ) -> None:
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            logger.error(f"Recipe with id {recipe_id} not found.")
            raise RecipeNotFoundException(recipe_id)

        existing_review = await self.review_repository.find_by_recipe_id_and_user_id(
            recipe_id, user_id
        )
        if not existing_review:
            logger.error(f"Review by user {user_id} for recipe {recipe_id} not found.")
            raise RecipeValidationException(
                f"Review by user {user_id} for recipe {recipe_id} not found."
            )

        updated_review = existing_review.update(update_data.rating, update_data.comment)
        await self.review_repository.save(updated_review)

        logger.info(
            f"Review by user {user_id} for recipe {recipe_id} updated successfully."
        )
