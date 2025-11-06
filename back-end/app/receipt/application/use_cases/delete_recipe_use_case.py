import logging
from typing import Optional
from app.auth.domain.user import UserId
from app.receipt.domain.interfaces import RecipeRepository
from app.receipt.application.exceptions import RecipeNotFoundException
from app.receipt.domain.entities.value_objects import RecipeId
from ..dtos import RecipeDeletedResponse
from .use_cases import DeleteRecipeUseCase


logger = logging.getLogger(__name__)


class DeleteRecipeUseCaseImpl(DeleteRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, author_id: Optional[UserId]
    ) -> RecipeDeletedResponse:
        logger.info(f"Executing DeleteRecipeUseCase for recipe_id: {recipe_id}")
        if author_id:
            logger.info(f"Author ID provided: {author_id}")
            recipe = await self.recipe_repository.get_by_id_and_author(
                recipe_id, author_id
            )
        else:
            logger.info("No Author ID provided")
            recipe = await self.recipe_repository.get_by_id(recipe_id)

        if not recipe:
            raise RecipeNotFoundException("recipe not found for delete")
        logger.info(f"Recipe found for delete: {recipe.id}")

        recipe.soft_delete()
        logger.info(f"Recipe soft deleted: {recipe.id}")
        await self.recipe_repository.save(recipe)

        logger.info(f"Recipe soft deleted: {recipe.id}")
        return RecipeDeletedResponse(id=recipe_id.value)
