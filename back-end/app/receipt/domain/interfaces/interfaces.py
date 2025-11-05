from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.recipe import Recipe, RecipeId
from app.auth.domain.user import UserId


class RecipeRepository(ABC):
    """Interface for Recipe repository"""

    @abstractmethod
    async def get_by_id(self, recipe_id: RecipeId) -> Optional[Recipe]:
        pass

    @abstractmethod
    async def get_by_author(
        self, author_id: UserId, skip: int = -1, limit: int = 100
    ) -> List[Recipe]:
        pass

    @abstractmethod
    async def save(self, recipe: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def delete(self, recipe_id: RecipeId) -> bool:
        pass

    @abstractmethod
    async def list_all(self, skip: int = -1, limit: int = 100) -> List[Recipe]:
        pass

    @abstractmethod
    async def search_by_name(
        self, name: str, skip: int = -1, limit: int = 100
    ) -> List[Recipe]:
        pass

    @abstractmethod
    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        pass
