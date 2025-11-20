import logging

from app.modules.auth.domain.interfaces import UserRepository
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import CreateRecipeUseCase
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    DifficultyLevel,
    CuisineType,
    RecipeCreateBasicInfo,
    RecipeCreateContent,
    RecipeCreateDetails,
    RecipeId,
)
from app.modules.recipe.application.dtos import (
    CreateRecipeRequest,
    RecipeCreatedResponse,
)
from app.modules.recipe.application.exceptions import RecipeValidationException
from app.modules.auth.application.exceptions import UserNotFoundException

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
        logger.info(f"Creating recipe '{request.name}' for author ID {author_id}")

        await self._validate_author(request.name, author_id)
        logger.info(f"Author ID {author_id} validated successfully")

        recipe = self._create_recipe(request, author_id)
        logger.info(f"Recipe '{request.name}' created")

        saved_recipe = await self.recipe_repository.save(recipe)

        logger.info(f"Recipe '{request.name}' saved with ID {saved_recipe.id}")
        return RecipeCreatedResponse(id=saved_recipe.id.value, name=saved_recipe.name)

    def _create_recipe(self, request: CreateRecipeRequest, author_id: UserId) -> Recipe:
        basic_info = RecipeCreateBasicInfo(
            name=request.name,
            author_id=author_id,
            description=request.description,
            difficulty=DifficultyLevel(request.difficulty),
            cuisine=CuisineType(request.cuisine),
        )

        createContent = RecipeCreateContent(
            ingredients=request.create_ingredients(),
            steps=request.create_steps(),
            tags=request.create_tags(),
        )

        details = RecipeCreateDetails(
            meal_types=request.create_meal_types(),
            serving_info=request.create_serving_info(),
            cooking_time=request.create_cooking_time(),
            nutritional_info=request.create_nutritional_info(),
        )

        return Recipe.create(
            basic_info=basic_info,
            content=createContent,
            details=details,
        )

    async def _validate_author(self, name: str, author_id: UserId):
        await self._validate_existing_author(author_id)
        await self._validate_not_duplicated_recipe(name, author_id)

    async def _validate_existing_author(self, author_id: UserId):
        author = await self.user_repository.exists_by_id(author_id)
        if not author:
            raise UserNotFoundException(f"Author with ID {author_id} not found")

    async def _validate_not_duplicated_recipe(self, name: str, author_id: UserId):
        if await self.recipe_repository.exists_by_name_and_author(name, author_id):
            raise RecipeValidationException(
                f"Recipe with name '{name}' already exists for this author",
                "DUPLICATE_RECIPE_NAME",
            )
