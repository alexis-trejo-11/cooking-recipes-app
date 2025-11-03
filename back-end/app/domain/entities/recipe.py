from dataclasses import dataclass, field
from typing import Optional, Set, List, Set
from decimal import Decimal
from .value_objects import *
from .enums import DifficultyLevel, CuisineType, MealType, DietType
from datetime import datetime, timezone
from .ingredient import Ingredient


class Recipe:
    def __init__(
        self,
        id: RecipeId,
        name: str,
        author_id: UserId,
        description: Optional[str] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        cuisine: Optional[CuisineType] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.author_id = author_id
        self.description = description
        self.difficulty = difficulty
        self.cuisine = cuisine

        # Collections
        self._ingredients: List[Ingredient] = []
        self._steps: List[Step] = []
        self._tags: Set[Tag] = set()

        # Metadata
        self._serving_info: Optional[ServingInfo] = None
        self._cooking_time: Optional[CookingTime] = None
        self._nutritional_info: Optional[NutritionalInfo] = None
        self._meal_types: Set[MealType] = set()

        # Tracking
        self._rating_sum: int = 0
        self._rating_count: int = 0
        self._view_count: int = 0
        self._favorite_count: int = 0
        self.version: int = 1

        # Timestamps
        self._created_at: datetime = datetime.now(timezone.utc)
        self._updated_at: datetime = datetime.now(timezone.utc)
        self.deleted_at: Optional[datetime] = None

    def record_update(self):
        datetime.now(timezone.utc)

    def add_ingredient(self, ingredient: Ingredient) -> None:
        if any(i.id == ingredient.id for i in self._ingredients):
            raise ValueError(f"Ingredient {ingredient.name} already exists in recipe")

        self._ingredients.append(ingredient)
        self.record_update()

    def remove_ingredient(self, ingredient_id: IngredientId):
        self._ingredients = [i for i in self._ingredients if i.id != ingredient_id]
        self.record_update()

    def get_ingredients(self) -> List[Ingredient]:
        return self._ingredients.copy()

    def get_required_ingredients(self) -> List[Ingredient]:
        """Get only non-optional ingredients"""
        return [i for i in self._ingredients if not i.is_optional]

    def add_step(
        self,
        description: str,
        duration_minutes: Optional[int] = None,
        technique: Optional[str] = None,
        temperature: Optional[str] = None,
    ) -> None:

        step = Step(
            number=len(self._steps) + 1,
            description=description,
            duration_minutes=duration_minutes,
            technique=technique,
            temperature=temperature,
        )

        self._steps.append(step)
        self.record_update()

    def get_step(self) -> List[Step]:
        return self._steps.copy()

    def reorder_stepts(self, new_order: List[Step]) -> None:
        """Reorder steps and renumber them"""
        if len(new_order) != len(self._steps):
            raise ValueError("New order must contain all steps")

        self._steps = [
            Step(
                number=i + 1,
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )
            for i, step in enumerate(new_order)
        ]
        self.record_update()

    def add_tag(self, tag: Tag) -> None:
        self._tags.add(tag)
        self.record_update()

    def remove_tags(self, tag: Tag) -> None:
        self._tags.discard(tag)
        self.record_update()

    def get_tags(self) -> Set[Tag]:
        return self._tags.copy()

    def add_meal_type(self, meal_type: MealType) -> None:
        self._meal_types.add(meal_type)
        self.record_update()

    def get_meal_types(self) -> Set[MealType]:
        return self._meal_types.copy()

    def set_serving_info(self, serving_info: ServingInfo) -> None:
        self._serving_info = serving_info
        self.record_update()

    def get_serving_info(self) -> Optional[ServingInfo]:
        return self._serving_info

    def set_cooking_time(self, cooking_time: CookingTime) -> None:
        self._cooking_time = cooking_time
        self.record_update()

    def get_cooking_time(self) -> Optional[CookingTime]:
        return self._cooking_time

    def calculate_total_time(self) -> int:
        """Calculate total time including prep and cooking"""
        if self._cooking_time:
            return self._cooking_time.total_minutes
        # Fallback to sum of step durations
        return sum(s.duration_minutes for s in self._steps if s.duration_minutes)

    def set_nutritional_info(self, nutritional_info: NutritionalInfo) -> None:
        self._nutritional_info = nutritional_info
        self.record_update()

    def get_nutritional_info(self) -> Optional[NutritionalInfo]:
        return self._nutritional_info

    def get_nutritional_info_per_serving(self) -> Optional[NutritionalInfo]:
        """Get nutritional info scaled to one serving"""
        if not self._nutritional_info or not self._serving_info:
            return None

        factor = Decimal(1) / Decimal(self._serving_info.servings)
        return self._nutritional_info.scale(factor)

    def is_suitable_for_diet(self, diet: DietType) -> bool:
        """Check if recipe is suitable for a specific diet"""
        return all(ingredient.is_suitable_for(diet) for ingredient in self._ingredients)

    def get_compatible_diets(self) -> Set[DietType]:
        """Get all diets this recipe is compatible with"""
        return {diet for diet in DietType if self.is_suitable_for_diet(diet)}

    def get_allergens(self) -> Set[str]:
        """Get a set of all allergens present in the recipe"""
        allergens: Set[str] = set()
        for ingredient in self._ingredients:
            allergens.update(ingredient.properties.allergens)
        return allergens

    # ========================================================================
    # Ratings and Tracking
    # ========================================================================

    def increment_view_count(self) -> None:
        self._view_count += 1
        self.record_update()

    def get_view_count(self) -> int:
        return self._view_count

    def increment_favorite_count(self) -> None:
        self._favorite_count += 1
        self.record_update()

    def get_favorite_count(self) -> int:
        return self._favorite_count

    # ========================================================================
    # Metadata
    # ========================================================================

    def get_created_at(self) -> datetime:
        return self._created_at

    def get_updated_at(self) -> datetime:
        return self._updated_at
