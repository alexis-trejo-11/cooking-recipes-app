import logging
from typing import Optional
from decimal import Decimal

from app.modules.auth.domain.interfaces import UserRepository
from app.modules.auth.application.exceptions import UserNotFoundException
from app.modules.auth.domain.user import UserId

from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    DifficultyLevel,
    CuisineType,
    RecipeId,
)

from ..dtos import CreateRecipeRequest, RecipeCreatedResponse, RecipeDeletedResponse
from ..exceptions import RecipeNotFoundException, RecipeValidationException
from ....auth.domain.user import UserId
from ..dtos import (
    RecipeUpdatedResponse,
    UpdateRecipeRequest,
    AddRatingRequest,
    RatingAddedResponse,
)
from .base import (
    UpdateRecipeUseCase,
    AddRatingUseCase,
    CreateRecipeUseCase,
    IncrementViewCountUseCase,
    DeleteRecipeUseCase,
    IncreaseFavoriteUseCase,
    DecreaseFavoriteUseCase,
    RestoreRecipeUseCase,
)

logger = logging.getLogger(__name__)


class CreateRecipeUseCaseImpl(CreateRecipeUseCase):
    def __init__(
        self, recipe_repository: RecipeRepository, user_repository: UserRepository
    ) -> None:
        self.recipe_repository = recipe_repository
        self.user_repository = user_repository

    async def execute(
        self, request: CreateRecipeRequest, author_id: UserId
    ) -> RecipeCreatedResponse:
        await self._validate_author(request.name, author_id)

        recipe = self.create_recipe(request, author_id)
        saved_recipe = await self.recipe_repository.save(recipe)

        return RecipeCreatedResponse(id=saved_recipe.id.value, name=saved_recipe.name)

    async def _validate_author(self, name: str, author_id: UserId):
        await self._validate_existing_author(author_id)
        await self._validate_not_duplicated_author(name, author_id)

    async def _validate_existing_author(self, author_id: UserId):
        author = await self.user_repository.exists_by_id(author_id)
        if not author:
            raise UserNotFoundException(f"Author with ID {author_id} not found")

    async def _validate_not_duplicated_author(self, name: str, author_id: UserId):
        if await self.recipe_repository.exists_by_name_and_author(name, author_id):
            raise RecipeValidationException(
                f"Recipe with name '{name}' already exists for this author",
                "DUPLICATE_RECIPE_NAME",
            )

    def create_recipe(self, request: CreateRecipeRequest, author_id: UserId) -> Recipe:
        # Create Value Objects
        ingredients = request.create_ingredients()
        steps = request.create_steps()
        tags = request.create_tags()
        meal_types = request.create_meal_types()
        serving_info = request.create_serving_info()
        cooking_time = request.create_cooking_time()
        nutritional_info = request.create_nutritional_info()

        recipe = Recipe.create(
            name=request.name,
            author_id=author_id,
            description=request.description,
            difficulty=DifficultyLevel(request.difficulty),
            cuisine=CuisineType(request.cuisine),
            meal_types=meal_types,
            serving_info=serving_info,
            cooking_time=cooking_time,
            nutritional_info=nutritional_info,
        )
        recipe.add_ingredients(ingredients)
        recipe.add_steps(steps)
        recipe.add_tags(tags)

        return recipe


class UpdateRecipeUseCaseImpl(UpdateRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, request: UpdateRecipeRequest, user_id: UserId
    ) -> RecipeUpdatedResponse:
        recipe = await self.recipe_repository.find_by_id_and_author(recipe_id, user_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.update_basic_info(
            name=request.name,
            description=request.description,
            cuisine=CuisineType(request.cuisine),
            difficulty=DifficultyLevel(request.difficulty),
        )
        serving_info = request.create_serving_info()
        cooking_time = request.create_cooking_time()
        nutritional_info = request.create_nutritional_info()
        steps = request.create_steps()
        ingredients = request.create_ingredients()
        tags = request.create_tags()
        meal_types = request.create_meal_types()

        if ingredients is not None:
            recipe.update_ingredients(ingredients)
        if steps is not None:
            recipe.update_steps(steps)
        if tags is not None:
            recipe.update_tags(tags)
        if meal_types is not None:
            recipe.update_meal_types(meal_types)
        if serving_info:
            recipe.update_serving_info(serving_info)
        if cooking_time:
            recipe.update_cooking_time(cooking_time)
        if nutritional_info:
            recipe.update_nutritional_info(nutritional_info)

        recipe_updated = await self.recipe_repository.save(recipe)
        return RecipeUpdatedResponse(
            id=recipe_updated.id.value,
            name=recipe_updated.name,
            version=recipe_updated.version,
        )


class AddRatingUseCaseImpl(AddRatingUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, request: AddRatingRequest, user_id: UserId
    ) -> RatingAddedResponse:
        logger.info(f"User {user_id} is adding rating to Recipe {recipe_id}")
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        logger.info(
            f"Adding rating {request.rating} to Recipe {recipe_id} by User {user_id}"
        )
        recipe.add_rating(request.rating)

        logger.info(
            f"New average rating for Recipe {recipe_id} is {recipe.average_rating}"
        )
        await self.recipe_repository.save(recipe)

        logger.info(f"User {user_id} has added a rating to Recipe {recipe_id}")
        return RatingAddedResponse(
            recipe_id=recipe.id.value,
            new_average_rating=Decimal(str(recipe.average_rating)),
            total_ratings=recipe.favorite_count,
        )


class IncrementViewCountUseCaseImpl(IncrementViewCountUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: int) -> None:
        logger.info(f"Incrementing view count for Recipe {recipe_id}")
        recipe = await self.recipe_repository.find_by_id(RecipeId(recipe_id))
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.increment_view_count()
        await self.recipe_repository.save(recipe)
        logger.info(
            f"View count for Recipe {recipe_id} incremented to {recipe.view_count}"
        )


# TODO: Implement ScaleRecipeUseCaseImpl
class DeleteRecipeUseCaseImpl(DeleteRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, author_id: Optional[UserId]
    ) -> RecipeDeletedResponse:
        logger.info(f"Executing DeleteRecipeUseCase for recipe_id: {recipe_id}")

        recipe = await self._get_recipe_or_raise(recipe_id, author_id)
        recipe.soft_delete()

        logger.info(f"Recipe soft deleted: {recipe.id}")
        await self.recipe_repository.save(recipe)

        logger.info(f"Recipe soft deleted: {recipe.id}")
        return RecipeDeletedResponse(id=recipe_id.value)

    async def _get_recipe_or_raise(
        self, recipe_id: RecipeId, author_id: Optional[UserId]
    ) -> "Recipe":
        if author_id:
            logger.info(f"Author ID provided: {author_id}")
            recipe = await self.recipe_repository.find_by_id_and_author(
                recipe_id, author_id
            )
        else:
            logger.info("No Author ID provided")
            recipe = await self.recipe_repository.find_by_id(recipe_id)

        if not recipe:
            raise RecipeNotFoundException("recipe not found for delete")
        logger.info(f"Recipe found for delete: {recipe.id}")

        return recipe


class IncreaseFavoriteUseCaseImpl(IncreaseFavoriteUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        logger.info(
            f"Executing IncreaseFavoriteUseCase for recipe_id: {recipe_id} by user_id: {user_id}"
        )

        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.increase_favorite_count()

        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe {recipe_id} favorite status toggled for user {user_id}")


class DecreaseFavoriteUseCaseImpl(DecreaseFavoriteUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        logger.info(
            f"Executing DecreaseFavoriteUseCase for recipe_id: {recipe_id} by user_id: {user_id}"
        )

        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.decrease_favorite_count()

        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe {recipe_id} favorite status toggled for user {user_id}")


class RestoreRecipeUseCaseImpl(RestoreRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId, author_id: UserId) -> None:
        logger.info(
            f"Executing RestoreRecipeUseCase for recipe_id: {recipe_id} by author_id: {author_id}"
        )

        recipe = await self.recipe_repository.find_by_id_and_author(
            recipe_id, author_id
        )
        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found")

        recipe.restore()

        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe {recipe_id} restored by author {author_id}")
