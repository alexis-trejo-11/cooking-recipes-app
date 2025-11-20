import logging

from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeReviewRepository,
)
from app.modules.recipe.application.use_cases.base import DeleteReviewUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.exceptions import RecipeNotFoundException

logger = logging.getLogger(__name__)


class DeleteReviewUseCaseImpl(DeleteReviewUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        review_repository: RecipeReviewRepository,
    ):
        self.recipe_repository = recipe_repository
        self.review_repository = review_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        logger.info(f"User {user_id} is deleting review for Recipe {recipe_id}")
        recipe = await self.recipe_repository.find_by_id(recipe_id)

        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        await self.review_repository.delete(recipe_id, user_id)
        logger.info(f"User {user_id} has deleted review for Recipe {recipe_id}")
