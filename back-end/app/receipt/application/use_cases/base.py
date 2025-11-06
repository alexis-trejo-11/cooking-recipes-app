from abc import ABC, abstractmethod
from app.utils.pagination import Page
from app.utils.page_request import PydanticPageRequest
from typing import Optional, List
from ..dtos import *
from app.auth.domain.user import UserId
from app.receipt.domain.entities.recipe import RecipeId


class CreateRecipeUseCase(ABC):
    @abstractmethod
    async def execute(
        self, request: CreateRecipeRequest, author_id: UserId
    ) -> RecipeCreatedResponse:
        pass


class GetRecipeUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id_int: int) -> Optional[RecipeResponse]:
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


class SearchRecipesUseCase(ABC):
    @abstractmethod
    async def execute(
        self, request: RecipeSearchRequest
    ) -> Page[RecipeSummaryResponse]:
        pass


class FindRecipesByIngredientsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, request: FindByIngredientsRequest, page_request: PydanticPageRequest
    ) -> Page[RecipeSummaryResponse]:
        pass


class ScaleRecipeUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: int, request: ScaleRecipeRequest, user_id: int
    ) -> RecipeScaledResponse:
        pass


class AddRatingUseCase(ABC):
    @abstractmethod
    async def execute(
        self, recipe_id: int, request: AddRatingRequest, user_id: int
    ) -> RatingAddedResponse:
        pass


class IncrementViewCountUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: int) -> None:
        pass


class ToggleFavoriteUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: int, user_id: int) -> bool:
        """Returns True if added to favorites, False if removed"""
        pass


class GetUserRecipesUseCase(ABC):
    @abstractmethod
    async def execute(
        self, author_id_int: int, page_request: PydanticPageRequest
    ) -> Page[RecipeSummaryResponse]:
        pass


class GetRecipeCompatibleDietsUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: int) -> List[DietType]:
        pass


class GetRecipeAllergensUseCase(ABC):
    @abstractmethod
    async def execute(self, recipe_id: int) -> List[str]:
        pass
