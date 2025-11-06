from dataclasses import dataclass
from datetime import datetime
from typing import Set
from app.auth.domain.user import UserId
from app.utils.core.specification import Specification
from app.receipt.domain.entities.recipe import (
    Recipe,
    DifficultyLevel,
    CuisineType,
    Tag,
    MealType,
)


@dataclass
class RecipeByNameSpecification(Specification):
    """Specification to filter recipes by name (partial match)."""

    name_pattern: str

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return self.name_pattern.lower() in candidate.name.lower()


@dataclass
class RecipeByAuthorSpecification(Specification):
    """Specification to filter recipes by author."""

    author_id: UserId

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return candidate.author_id == self.author_id


@dataclass
class RecipeByDifficultySpecification(Specification):
    """Specification to filter recipes by difficulty level."""

    difficulty: DifficultyLevel

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return candidate.difficulty == self.difficulty


@dataclass
class RecipeByCuisineSpecification(Specification):
    """Specification to filter recipes by cuisine type."""

    cuisine: CuisineType

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return candidate.cuisine == self.cuisine


@dataclass
class RecipeByTagsSpecification(Specification):
    """Specification to filter recipes that have ALL the specified tags."""

    tags: Set[Tag]

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return self.tags.issubset(candidate._tags)


@dataclass
class RecipeByAnyTagSpecification(Specification):
    """Specification to filter recipes that have ANY of the specified tags."""

    tags: Set[Tag]

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return bool(self.tags & candidate._tags)


@dataclass
class RecipeByMealTypeSpecification(Specification):
    """Specification to filter recipes by meal type."""

    meal_types: Set[MealType]

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return bool(self.meal_types & candidate._meal_types)


@dataclass
class RecipeByIngredientSpecification(Specification):
    """Specification to filter recipes that contain ingredients with the given name."""

    ingredient_name: str

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        # Asumiendo que Ingredient tiene un atributo 'name'
        return any(
            self.ingredient_name.lower() in ing.name.lower()
            for ing in candidate._ingredients
        )


@dataclass
class RecipeByMinRatingSpecification(Specification):
    """Specification to filter recipes with minimum rating."""

    min_rating: float

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        if candidate._rating_count == 0:
            return False
        rating = candidate._rating_sum / candidate._rating_count
        return rating >= self.min_rating


@dataclass
class RecipeIsActiveSpecification(Specification):
    """Specification to filter only active (non-deleted) recipes."""

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return candidate.deleted_at is None


@dataclass
class RecipeCreatedAfterSpecification(Specification):
    """Specification to filter recipes created after certain date."""

    date: datetime

    def is_satisfied_by(self, candidate: "Recipe") -> bool:
        return candidate._created_at and candidate._created_at >= self.date
