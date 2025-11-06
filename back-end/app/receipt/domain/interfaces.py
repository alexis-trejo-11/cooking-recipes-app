from abc import ABC, abstractmethod
from typing import Optional
from .models.entities.recipe import Recipe, RecipeId
from app.utils.core.specification import SQLSpecification as Specification
from app.auth.domain.user import UserId
from app.utils.core.pagination import Page, PageRequest


class RecipeRepository(ABC):
    """Interface for Recipe repository"""

    @abstractmethod
    async def find_by_id(self, recipe_id: RecipeId) -> Optional[Recipe]:
        pass

    @abstractmethod
    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        pass

    @abstractmethod
    async def search(
        self, spec: Specification, page_request: PageRequest
    ) -> Page[Recipe]:
        pass

    @abstractmethod
    async def save(self, recipe: Recipe) -> Recipe:
        pass

    @abstractmethod
    async def delete(self, recipe_id: RecipeId) -> bool:
        pass

    @abstractmethod
    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        pass
