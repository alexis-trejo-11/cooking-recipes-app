"""
Repository implementations for the recipe module.

This package contains SQLAlchemy implementations of all repository interfaces
defined in the domain layer, following the Repository Pattern and
Dependency Inversion Principle.

Structure:
- base.py: Common base classes and utilities
- recipe_repository.py: Main recipe aggregate repository
- favorite_repository.py: Recipe favorite operations
- review_repository.py: Recipe review operations
- internal/: Internal repositories for aggregate entities

The repositories in this package provide:
1. Data persistence using SQLAlchemy ORM
2. Transaction management and error handling
3. Efficient querying with pagination and filtering
4. Aggregate root consistency enforcement
5. Proper relationship management

All repositories are designed to be used with async/await patterns
and integrate seamlessly with FastAPI's dependency injection system.
"""

from .recipe_repository import SqlAlchemyRecipeRepository
from .favorite_repository import SqlAlchemyRecipeFavoriteRepository
from .review_repository import SqlAlchemyRecipeReviewRepository

# Re-export internal repositories for testing or special use cases
from .internal import (
    MealTypeRepository,
    IngredientRepository,
    StepRepository,
    TagRepository,
)

__all__ = [
    # Main repository implementations
    "SqlAlchemyRecipeRepository",
    "SqlAlchemyRecipeFavoriteRepository",
    "SqlAlchemyRecipeReviewRepository",
    # Internal repositories (for testing or advanced usage)
    "MealTypeRepository",
    "IngredientRepository",
    "StepRepository",
    "TagRepository",
]
