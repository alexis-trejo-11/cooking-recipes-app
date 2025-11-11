from typing import List
from abc import ABC, abstractmethod
from app.utils.external.page_request import PydanticPaginationParams
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import RecipeSearchRequest
from ..dtos import *


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
    async def execute(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> RecipeDeletedResponse:
        pass


class ScaleRecipeUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: RecipeId, request: ScaleRecipeRequest, user_id: int
    ) -> RecipeScaledResponse:
        pass


class AddRatingUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: RecipeId, request: AddRatingRequest, user_id: UserId
    ) -> RatingAddedResponse:
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
