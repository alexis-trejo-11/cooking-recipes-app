"""
Domain layer interfaces for recipe repositories.

These interfaces define the contracts that infrastructure implementations
must satisfy. They keep the domain layer independent of persistence details.
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.utils.core.pagination import Page, PaginationParams
from app.utils.core.specification import Specification
from app.modules.recipe.domain.models.entities.recipe import Recipe, RecipeId
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.review import Review


class RecipeRepository(ABC):
    """
    Repository interface for Recipe aggregate.

    This repository handles persistence operations for the Recipe aggregate root
    and its associated entities (ingredients, steps, tags, meal types).
    """

    @abstractmethod
    async def find_by_id(
        self,
        recipe_id: RecipeId,
        include_deleted: bool = False,
        with_relations: bool = False,
    ) -> Optional[Recipe]:
        """
        Find recipe by its identifier.

        Args:
            recipe_id: Recipe identifier
            include_deleted: Whether to include soft-deleted recipes
            with_relations: Whether to eagerly load relationships

        Returns:
            Recipe entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_featured_recipes(self, limit: int) -> list[Recipe]:
        """
        Find featured recipes for display on the homepage.

        Args:
            limit: Maximum number of featured recipes to retrieve
        Returns:
            List of featured Recipe entities
        """
        pass

    @abstractmethod
    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        """
        Find recipe by ID and author (for authorization checks).

        Args:
            recipe_id: Recipe identifier
            author_id: Author user identifier

        Returns:
            Recipe entity if found and belongs to author, None otherwise
        """
        pass

    @abstractmethod
    async def find_favorites_by_user_id(
        self,
        user_id: UserId,
        page_request: PaginationParams,
    ) -> Page[Recipe]:
        """
        Find favorite recipes by user with pagination.
        Args:
            user_id: User identifier
            page_request: Pagination parameters
        Returns:
            Paginated list of favorite recipes by the user
        """
        pass

    @abstractmethod
    async def search(
        self, spec: Specification, page_request: PaginationParams
    ) -> Page[Recipe]:
        """
        Search recipes using specification pattern.

        Args:
            spec: Search specification with filters
            page_request: Pagination parameters

        Returns:
            Paginated results
        """
        pass

    @abstractmethod
    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        """
        Check if recipe with given name exists for author.

        Args:
            name: Recipe name
            author_id: Author user identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def exists_by_id(
        self, recipe_id: RecipeId, include_deleted: bool = False
    ) -> bool:
        """
        Check if recipe exists by ID.

        Args:
            recipe_id: Recipe identifier
            include_deleted: Whether to include soft-deleted recipes

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def save(self, recipe: Recipe) -> Recipe:
        """
        Save recipe (create or update).

        Args:
            recipe: Recipe entity to save

        Returns:
            Saved recipe entity with updated data
        """
        pass

    @abstractmethod
    async def delete(self, recipe_id: RecipeId) -> bool:
        """
        Soft delete recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def increase_view_count(self, recipe_id: RecipeId) -> None:
        """
        Increment view count for a recipe.

        Args:
            recipe_id: Recipe identifier
        """
        pass


class RecipeFavoriteRepository(ABC):
    """
    Repository interface for recipe favorite operations.

    Handles the many-to-many relationship between users and their favorite recipes.
    """

    @abstractmethod
    async def count_by_recipe(self, recipe_id: int) -> int:
        """
        Count how many users have favorited a recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Number of favorites
        """
        pass

    @abstractmethod
    async def toggle(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Toggle favorite status for a user.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Returns:
            True if favorite was added, False if removed
        """
        pass

    @abstractmethod
    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Check if recipe is favorited by user.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier

        Returns:
            True if favorited, False otherwise
        """
        pass


class RecipeReviewRepository(ABC):
    """
    Repository interface for recipe review operations.

    Handles user reviews and ratings for recipes.
    """

    @abstractmethod
    async def find_by_recipe_id(
        self, recipe_id: RecipeId, page_request: PaginationParams
    ) -> Page[Review]:
        """
        Find reviews by recipe ID with pagination.

        Args:
            recipe_id: Recipe identifier
            page_request: Pagination parameters

        Returns:
            Paginated list of reviews for the recipe
        """
        pass

    @abstractmethod
    async def find_by_recipe_id_and_user_id(
        self, recipe_id: RecipeId, user_id: UserId
    ) -> Optional[Review]:
        """
        Find a review by recipe ID and user ID.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier
        Returns:
            Review entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Check if a user has reviewed a recipe.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier
        Returns:
            True if review exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_recipe(self, recipe_id: int) -> int:
        """
        Count reviews for a recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Number of reviews
        """
        pass

    @abstractmethod
    async def save(self, review: Review) -> None:
        """
        Create or update a review.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier
            rating: Rating value (1-5)
            comment: Optional review comment
        """
        pass

    @abstractmethod
    async def delete(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """
        Delete a user's review for a recipe.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier
        """
        pass
