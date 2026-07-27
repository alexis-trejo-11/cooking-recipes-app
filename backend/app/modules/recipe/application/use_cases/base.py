from abc import ABC, abstractmethod
from typing import List

from app.utils.external.page_request import PydanticPaginationParams
from app.utils.core.pagination import Page, PaginationParams
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.recipe.application.dtos import (
    RecipeSearchRequest,
    RecipeUpdatedResponse,
    RecipeCreatedResponse,
    CreateRecipeRequest,
    RecipeSummaryResponse,
    ReviewPageResponse,
    ReviewResponse,
    UpdateRecipeRequest,
    RecipePageResponse,
    RecipeResponse,
    ReviewCreatedResponse,
    CreateReviewRequest,
    UpdateReviewRequest,
)

# Recipe Use Cases


class SearchRecipesUseCase(ABC):
    @abstractmethod
    async def execute(self, request: RecipeSearchRequest) -> RecipePageResponse:
        pass


class GetFeaturedRecipesUseCase(ABC):
    @abstractmethod
    async def execute(self) -> List[RecipeSummaryResponse]:
        pass


class GetUserRecipesUseCase(ABC):
    @abstractmethod
    async def execute(
        self, author_id: UserId, page_params: PydanticPaginationParams
    ) -> RecipePageResponse:
        pass


class GetUserFavoritesRecipesUseCase(ABC):
    @abstractmethod
    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        pass


class GetRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> RecipeResponse:
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


class RestoreRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> None:
        pass


class DeleteRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, author_id: UserId) -> None:
        pass


# Review Use Cases


class GetUserReviewForRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> ReviewResponse:
        pass


class GetRecipeReviewsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: RecipeId, page_request: PaginationParams
    ) -> ReviewPageResponse:
        pass


class CreateReviewUseCase(ABC):
    @abstractmethod
    async def execute(
        self, request: CreateReviewRequest, user_id: UserId, recipe_id: RecipeId
    ) -> ReviewCreatedResponse:
        pass


class UpdateReviewUseCase(ABC):
    @abstractmethod
    async def execute(
        self, user_id: UserId, recipe_id: RecipeId, update_data: UpdateReviewRequest
    ) -> None:
        pass


class DeleteReviewUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        pass


class IncrementViewCountUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId) -> None:
        pass


# Favorite Use Cases


class ToggleFavoriteUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> None:
        pass


class IsFavoriteUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        pass


class GetRecipeFavoritesByUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self, user_id: UserId, page_request: PaginationParams
    ) -> Page[RecipeSummaryResponse]:
        pass
