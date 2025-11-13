import logging
from typing import List
from abc import ABC, abstractmethod
from app.utils.external.page_request import PydanticPaginationParams
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import RecipeSearchRequest
from typing import Optional
from decimal import Decimal
from app.modules.auth.domain.interfaces import UserRepository
from app.modules.auth.application.exceptions import UserNotFoundException
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeFavoriteRepository,
    RecipeReviewRepository,
)
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    DifficultyLevel,
    CuisineType,
    DietType,
    RecipeId,
    UserId,
    RecipeCreateBasicInfo,
    RecipeCreateContent,
    RecipeCreateDetails,
)
from .exceptions import RecipeNotFoundException, RecipeValidationException
from .dtos import (
    PydanticPaginationParams,
    RecipeUpdatedResponse,
    RecipeCreatedResponse,
    CreateRecipeRequest,
    RecipeSummaryResponse,
    RecipeSearchRequest,
    UpdateRecipeRequest,
    RecipePageResponse,
    RecipeResponse,
    ReviewCreatedResponse,
    CreateReviewRequest,
)
from app.modules.recipe.infrastructure.persistence.specification_builder import (
    RecipeSearchCriteria,
    RecipeSpecificationBuilder,
    Specification,
)
from app.utils.core.pagination import Page, PaginationParams

logger = logging.getLogger("app.modules.recipe")


class SearchRecipesUseCase(ABC):
    @abstractmethod
    async def execute(self, request: RecipeSearchRequest) -> RecipePageResponse:
        """
        Execute recipe search with various filters.

        Args:
            request: Search criteria and pagination parameters

        Returns:
            RecipePageResponse: Paginated search results

        Raises:
            ValueError: If search criteria are invalid
        """
        pass


class GetUserRecipesUseCase(ABC):
    @abstractmethod
    async def execute(
        self, author_id: UserId, page_params: PydanticPaginationParams
    ) -> RecipePageResponse:
        """
        Get paginated recipes for a specific user.

        Args:
            author_id: Author ID as UserId
            page_params: Pagination parameters

        Returns:
            RecipePageResponse: Paginated user recipes

        Raises:
            ValueError: If author ID is invalid
        """
        pass


class GetRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> RecipeResponse:
        pass


class GetRecipeCompatibleDietsUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> List[DietType]:
        pass


class GetRecipeAllergensUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> List[str]:
        pass


class CreateRecipeUseCase(ABC):
    @abstractmethod
    async def execute(
        self, request: CreateRecipeRequest, author_id: UserId
    ) -> RecipeCreatedResponse:
        pass


class UpdateRecipeUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: RecipeId, request: UpdateRecipeRequest, user_id: UserId
    ) -> RecipeUpdatedResponse:
        pass


class DeleteRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, author_id: UserId) -> None:
        pass


class CreateReviewUseCase(ABC):
    @abstractmethod
    async def execute(self, request: CreateReviewRequest) -> ReviewCreatedResponse:
        pass


class DeleteReviewUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Deletes a review by its ID."""
        pass


class IncrementViewCountUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> None:
        """Increments the view count for a recipe."""
        pass


class ToggleFavoriteUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Toggles the favorite status for a recipe."""
        pass


class RestoreRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> None:
        """Restores a soft-deleted recipe."""
        pass


class GetRecipeUseCaseImpl(GetRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> RecipeResponse:
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        return RecipeResponse.from_recipe(recipe)


class GetRecipeFavoritesByUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        pass


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

        recipe = self.create_recipe(request, author_id)
        logger.info(f"Recipe '{request.name}' created ")

        saved_recipe = await self.recipe_repository.save(recipe)

        logger.info(f"Recipe '{request.name}' saved with ID {saved_recipe.id}")
        return RecipeCreatedResponse(id=saved_recipe.id.value, name=saved_recipe.name)

    def create_recipe(self, request: CreateRecipeRequest, author_id: UserId) -> Recipe:
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


class UpdateRecipeUseCaseImpl(UpdateRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(
        self, recipe_id: RecipeId, request: UpdateRecipeRequest, user_id: UserId
    ) -> RecipeUpdatedResponse:
        recipe = await self.recipe_repository.find_by_id_and_author(recipe_id, user_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

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


class IncrementViewCountUseCaseImpl(IncrementViewCountUseCase):
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> None:
        logger.info(f"Incrementing view count for Recipe {recipe_id}")
        exists = await self.recipe_repository.exists_by_id(recipe_id)
        if not exists:
            raise RecipeNotFoundException(recipe_id)

        await self.recipe_repository.increase_view_count(recipe_id)
        logger.info(f"View count for Recipe {recipe_id} incremented successfully")


class RestoreRecipeUseCaseImpl(RestoreRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId) -> None:
        logger.info(f"Executing RestoreRecipeUseCase for recipe_id: {recipe_id}")

        recipe = await self.recipe_repository.find_by_id(
            include_deleted=True, recipe_id=recipe_id
        )
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        recipe.restore()

        await self.recipe_repository.save(recipe)
        logger.info(f"Recipe {recipe_id} restored")


class DeleteRecipeUseCaseImpl(DeleteRecipeUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(self, recipe_id: RecipeId, author_id: Optional[UserId]) -> None:
        logger.info(f"Executing DeleteRecipeUseCase for recipe_id: {recipe_id}")

        recipe = await self._get_recipe_or_raise(recipe_id, author_id)
        recipe.soft_delete()

        logger.info(f"Recipe soft deleted: {recipe.id}")
        await self.recipe_repository.save(recipe)

        logger.info(f"Recipe soft deleted: {recipe.id}")

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
            raise RecipeNotFoundException(recipe_id)
        logger.info(f"Recipe found for delete: {recipe.id}")

        return recipe


class GetRecipeFavoritesByUserUseCaseImpl(GetRecipeFavoritesByUserUseCase):
    def __init__(self, recipe_repository: RecipeRepository) -> None:
        self.recipe_repository = recipe_repository

    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        logger.info(f"Fetching favorite recipes for user_id: {user_id}")

        recipe_page = await self.recipe_repository.find_favorites_by_user_id(
            user_id, page_request
        )
        return recipe_page.map(RecipeSummaryResponse.from_recipe)


class ToggleFavoriteUseCaseImpl(ToggleFavoriteUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        recipe_favorite_repository: RecipeFavoriteRepository,
    ) -> None:
        self.recipe_repository = recipe_repository
        self.recipe_favorite_repository = recipe_favorite_repository

    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        logger.info(
            f"Executing IncreaseFavoriteUseCase for recipe_id: {recipe_id} by user_id: {user_id}"
        )

        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        await self.recipe_favorite_repository.toggle(recipe_id, user_id)
        logger.info(f"Recipe {recipe_id} favorite status toggled for user {user_id}")


class CreateReviewUseCaseImpl(CreateReviewUseCase):
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        review_repository: RecipeReviewRepository,
    ):
        self.recipe_repository = recipe_repository
        self.review_repository = review_repository

    async def execute(self, request: CreateReviewRequest) -> ReviewCreatedResponse:
        logger.info(
            f"User {request.user_id} is adding review to Recipe {request.recipe_id}"
        )
        recipe_id = RecipeId(request.recipe_id)
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(recipe_id)

        existing_review = await self.review_repository.exists(
            recipe_id, UserId(request.user_id)
        )
        if existing_review:
            raise RecipeValidationException(
                f"User {request.user_id} has already reviewed Recipe {request.recipe_id}",
                "DUPLICATE_REVIEW",
            )

        review = request.to_domain()
        await self.review_repository.save(review)

        logger.info(
            f"User {request.user_id} review saved for Recipe {request.recipe_id}"
        )
        return ReviewCreatedResponse(
            recipe_id=review.recipe_id.value,
            new_average_rating=Decimal(
                str(recipe.average_rating) if recipe.average_rating else "0"
            ),
            total_ratings=recipe.review_count,
        )


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
