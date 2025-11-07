from typing import Optional, Set, List
from datetime import datetime
from dataclasses import dataclass

from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.value_objects.enums import (
    DifficultyLevel,
    CuisineType,
    MealType,
)
from .specification import *


@dataclass
class RecipeSearchCriteria:
    """DTO for recipe search criteria."""

    name: Optional[str] = None
    author_id: Optional[UserId] = None
    difficulty: Optional[DifficultyLevel] = None
    cuisine: Optional[CuisineType] = None
    tags: Optional[Set[str]] = None
    meal_types: Optional[Set[MealType]] = None
    ingredient_name: Optional[str] = None
    min_rating: Optional[float] = None
    max_cooking_time: Optional[int] = None
    created_after: Optional[datetime] = None
    include_deleted: bool = False


class RecipeSpecificationBuilder:
    """Builder for creating complex recipe specifications."""

    @staticmethod
    def build_from_criteria(criteria: RecipeSearchCriteria) -> Specification:
        """
        Build complex specification from search criteria.

        Args:
            criteria: Search criteria DTO

        Returns:
            Specification: Combined specification
        """
        # Start with active recipes unless explicitly including deleted
        if not criteria.include_deleted:
            spec = RecipeIsActiveSpecification()
        else:
            # If including deleted, we don't need the active filter
            spec = None

        # Add filters based on provided criteria
        if criteria.name:
            name_spec = RecipeByNameSpecification(criteria.name)
            spec = name_spec if spec is None else AndSpecification(spec, name_spec)

        if criteria.author_id:
            author_spec = RecipeByAuthorSpecification(criteria.author_id)
            spec = author_spec if spec is None else AndSpecification(spec, author_spec)

        if criteria.difficulty:
            difficulty_spec = RecipeByDifficultySpecification(criteria.difficulty)
            spec = (
                difficulty_spec
                if spec is None
                else AndSpecification(spec, difficulty_spec)
            )

        if criteria.cuisine:
            cuisine_spec = RecipeByCuisineSpecification(criteria.cuisine.value)
            spec = (
                cuisine_spec if spec is None else AndSpecification(spec, cuisine_spec)
            )

        if criteria.tags:
            tags_spec = RecipeByTagsSpecification(criteria.tags)
            spec = tags_spec if spec is None else AndSpecification(spec, tags_spec)

        if criteria.meal_types:
            meal_types_spec = RecipeByMealTypeSpecification(criteria.meal_types)
            spec = (
                meal_types_spec
                if spec is None
                else AndSpecification(spec, meal_types_spec)
            )

        if criteria.ingredient_name:
            ingredient_spec = RecipeByIngredientSpecification(criteria.ingredient_name)
            spec = (
                ingredient_spec
                if spec is None
                else AndSpecification(spec, ingredient_spec)
            )

        if criteria.min_rating:
            rating_spec = RecipeByMinRatingSpecification(criteria.min_rating)
            spec = rating_spec if spec is None else AndSpecification(spec, rating_spec)

        if criteria.max_cooking_time:
            time_spec = RecipeByMaxCookingTimeSpecification(criteria.max_cooking_time)
            spec = time_spec if spec is None else AndSpecification(spec, time_spec)

        if criteria.created_after:
            date_spec = RecipeCreatedAfterSpecification(criteria.created_after)
            spec = date_spec if spec is None else AndSpecification(spec, date_spec)

        if spec is None:
            if not criteria.include_deleted:
                return RecipeIsActiveSpecification()
            else:
                return RecipeIsActiveSpecification() or NotSpecification(
                    RecipeIsActiveSpecification()
                )

        return spec

    @staticmethod
    def build_complex_search(
        name: Optional[str] = None,
        author_id: Optional[UserId] = None,
        difficulty: Optional[DifficultyLevel] = None,
        tags: Optional[Set[str]] = None,
        min_rating: Optional[float] = None,
    ) -> Specification:
        """Convenience method for common search patterns."""
        criteria = RecipeSearchCriteria(
            name=name,
            author_id=author_id,
            difficulty=difficulty,
            tags=tags,
            min_rating=min_rating,
        )
        return RecipeSpecificationBuilder.build_from_criteria(criteria)
