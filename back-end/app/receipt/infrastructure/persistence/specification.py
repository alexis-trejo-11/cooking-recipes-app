from datetime import datetime
from sqlalchemy import and_, or_, func, String, Integer, DateTime
from sqlalchemy.orm import joinedload, aliased
from typing import Any, Set, List, Optional
from dataclasses import dataclass
from sqlalchemy import true
from app.utils.core.specification import SQLSpecification
from app.receipt.infrastructure.persistence.models import (
    RecipeModel,
    TagModel,
    recipe_tags,
    RecipeMealTypeModel,
    IngredientModel,
)
from app.receipt.domain.models.entities.recipe import Recipe, DifficultyLevel
from app.auth.domain.user import UserId
from app.receipt.domain.models.value_objects.enums import MealType, DietType


@dataclass
class AllSpecification(SQLSpecification):
    """
    Specification that matches all recipes (no filtering).
    Useful for listing all active recipes without any criteria.
    """

    include_deleted: bool = False

    def is_satisfied_by(self, candidate: Any) -> bool:
        """
        At domain level, this accepts all candidates.

        Args:
            candidate: The recipe to check

        Returns:
            True if recipe should be included
        """
        if self.include_deleted:
            return True
        # Only filter out deleted recipes
        return not getattr(candidate, "is_deleted", False)

    def to_sql_condition(self) -> Any:
        """
        Convert to SQL condition.

        Returns:
            SQL condition that matches all non-deleted recipes
        """
        if self.include_deleted:
            # Return a condition that's always true
            return true()

        # Only filter out deleted recipes
        return RecipeModel.deleted_at.is_(None)

    def get_joins(self) -> List[Any]:
        """
        No joins needed for this specification.

        Returns:
            Empty list as no joins are required
        """
        return []


@dataclass
class RecipeByNameSpecification(SQLSpecification):
    """Specification to filter recipes by name (partial match)."""

    name_pattern: str

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe name contains the pattern (domain level)."""
        return self.name_pattern.lower() in candidate.name.lower()

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.name.ilike(f"%{self.name_pattern}%")

    def get_joins(self):
        """No additional joins needed for name filter."""
        return []


@dataclass
class RecipeByAuthorSpecification(SQLSpecification):
    """Specification to filter recipes by author."""

    author_id: UserId

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe belongs to author (domain level)."""
        return candidate.author_id == self.author_id

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.author_id == self.author_id.value

    def get_joins(self):
        """No additional joins needed for author filter."""
        return []


@dataclass
class RecipeByDifficultySpecification(SQLSpecification):
    """Specification to filter recipes by difficulty level."""

    difficulty: DifficultyLevel

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe has specified difficulty (domain level)."""
        return candidate.difficulty == self.difficulty

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.difficulty == self.difficulty.value

    def get_joins(self):
        """No additional joins needed for difficulty filter."""
        return []


@dataclass
class RecipeByTagsSpecification(SQLSpecification):
    """Specification to filter recipes that have ALL the specified tags."""

    tags: Set[str]  # Tag names

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe has all specified tags (domain level)."""
        candidate_tag_names = {tag.name for tag in candidate.tags}
        return self.tags.issubset(candidate_tag_names)

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        if not self.tags:
            return True  # No filter if no tags specified

        # For multiple tags, we need to ensure recipe has ALL tags
        from sqlalchemy import exists, select

        conditions = []
        for tag_name in self.tags:
            # Subquery to check if recipe has this specific tag
            subquery = (
                select(1)
                .select_from(recipe_tags)
                .join(TagModel, recipe_tags.c.tag_id == TagModel.id)
                .where(
                    and_(
                        recipe_tags.c.recipe_id == RecipeModel.id,
                        TagModel.name == tag_name,
                    )
                )
                .exists()
            )
            conditions.append(subquery)

        return and_(*conditions)

    def get_joins(self):
        """Joins needed for tag filtering."""
        return []  # We use EXISTS subqueries instead of joins


@dataclass
class RecipeByAnyTagSpecification(SQLSpecification):
    """Specification to filter recipes that have ANY of the specified tags."""

    tags: Set[str]  # Tag names

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe has any of the specified tags (domain level)."""
        candidate_tag_names = {tag.name for tag in candidate.tags}
        return bool(self.tags & candidate_tag_names)

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        if not self.tags:
            return True  # No filter if no tags specified

        return RecipeModel.tags.any(TagModel.name.in_(self.tags))

    def get_joins(self):
        """Joins needed for tag filtering."""
        return [RecipeModel.tags]


@dataclass
class RecipeByMealTypeSpecification(SQLSpecification):
    """Specification to filter recipes by meal type."""

    meal_types: Set[MealType]

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe has any of the specified meal types (domain level)."""
        return bool(self.meal_types & candidate.meal_types)

    def to_satisfied_by(self):
        """Convert to SQL condition for database query."""
        if not self.meal_types:
            return True

        meal_type_values = [meal_type.value for meal_type in self.meal_types]
        return RecipeModel.meal_types.any(
            RecipeMealTypeModel.meal_type.in_(meal_type_values)
        )

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        if not self.meal_types:
            return True

        meal_type_values = [meal_type.value for meal_type in self.meal_types]
        return RecipeModel.meal_types.any(
            RecipeMealTypeModel.meal_type.in_(meal_type_values)
        )

    def get_joins(self):
        """Joins needed for meal type filtering."""
        return [RecipeModel.meal_types]


@dataclass
class RecipeByCuisineSpecification(SQLSpecification):
    """Specification to filter recipes by cuisine type."""

    cuisine: str

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe cuisine matches (domain level)."""
        return (
            candidate.cuisine is not None
            and candidate.cuisine.value.lower() == self.cuisine.lower()
        )

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return func.lower(RecipeModel.cuisine) == self.cuisine.lower()

    def get_joins(self):
        """No additional joins needed for cuisine filter."""
        return []


@dataclass
class RecipeByIngredientSpecification(SQLSpecification):
    """Specification to filter recipes that contain ingredients with the given name."""

    ingredient_name: str

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe contains ingredient with name (domain level)."""
        return any(
            self.ingredient_name.lower() in ingredient.name.lower()
            for ingredient in candidate.ingredients
        )

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.ingredients.any(
            IngredientModel.name.ilike(f"%{self.ingredient_name}%")
        )

    def get_joins(self):
        """Joins needed for ingredient filtering."""
        return [RecipeModel.ingredients]


@dataclass
class RecipeByMinRatingSpecification(SQLSpecification):
    """Specification to filter recipes with minimum rating."""

    min_rating: float

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe meets minimum rating (domain level)."""
        if candidate.rating_count == 0:
            return False
        rating = candidate._rating_sum / candidate._rating_count
        return rating >= self.min_rating

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        # Calculate average rating and filter
        return and_(
            RecipeModel.rating_count > 0,
            (RecipeModel.rating_sum / RecipeModel.rating_count) >= self.min_rating,
        )

    def get_joins(self):
        """No additional joins needed for rating filter."""
        return []


@dataclass
class RecipeIsActiveSpecification(SQLSpecification):
    """Specification to filter only active (non-deleted) recipes."""

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe is not deleted (domain level)."""
        return not candidate.is_deleted

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.deleted_at.is_(None)

    def get_joins(self):
        """No additional joins needed for active filter."""
        return []


@dataclass
class RecipeCreatedAfterSpecification(SQLSpecification):
    """Specification to filter recipes created after certain date."""

    date: datetime

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe was created after date (domain level)."""
        return candidate.created_at >= self.date

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        return RecipeModel.created_at >= self.date

    def get_joins(self):
        """No additional joins needed for date filter."""
        return []


@dataclass
class RecipeByMaxCookingTimeSpecification(SQLSpecification):
    """Specification to filter recipes with maximum cooking time."""

    max_minutes: int

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if recipe cooking time is within limit (domain level)."""
        total_time = candidate.calculate_total_time()
        return total_time <= self.max_minutes

    def to_sql_condition(self):
        """Convert to SQL condition for database query."""
        # Calculate total time from prep + cook + rest
        total_time = (
            func.coalesce(RecipeModel.prep_time_minutes, 0)
            + func.coalesce(RecipeModel.cook_time_minutes, 0)
            + func.coalesce(RecipeModel.rest_time_minutes, 0)
        )

        return total_time <= self.max_minutes

    def get_joins(self):
        """No additional joins needed for cooking time filter."""
        return []


# Composite SQL Specifications
@dataclass
class AndSQLSpecification(SQLSpecification):
    """AND combination of SQL specifications."""

    first: SQLSpecification
    second: SQLSpecification

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if candidate satisfies both specifications (domain level)."""
        return self.first.is_satisfied_by(candidate) and self.second.is_satisfied_by(
            candidate
        )

    def to_sql_condition(self):
        """Combine SQL conditions with AND."""
        return and_(self.first.to_sql_condition(), self.second.to_sql_condition())

    def get_joins(self):
        """Combine joins from both specifications."""
        return self.first.get_joins() + self.second.get_joins()


@dataclass
class OrSQLSpecification(SQLSpecification):
    """OR combination of SQL specifications."""

    first: SQLSpecification
    second: SQLSpecification

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if candidate satisfies either specification (domain level)."""
        return self.first.is_satisfied_by(candidate) or self.second.is_satisfied_by(
            candidate
        )

    def to_sql_condition(self):
        """Combine SQL conditions with OR."""
        return or_(self.first.to_sql_condition(), self.second.to_sql_condition())

    def get_joins(self):
        """Combine joins from both specifications."""
        return self.first.get_joins() + self.second.get_joins()


@dataclass
class NotSQLSpecification(SQLSpecification):
    """NOT specification for SQL criteria."""

    spec: SQLSpecification

    def is_satisfied_by(self, candidate: Recipe) -> bool:
        """Check if candidate does not satisfy specification (domain level)."""
        return not self.spec.is_satisfied_by(candidate)

    def to_sql_condition(self):
        """Negate SQL condition."""
        return not_(self.spec.to_sql_condition())

    def get_joins(self):
        """Use same joins as the original specification."""
        return self.spec.get_joins()
