from typing import Optional, Set, List
from decimal import Decimal, InvalidOperation
import logging
from .value_objects import *
from .enums import DifficultyLevel, CuisineType, MealType, DietType
from datetime import datetime, timezone
from .ingredient import Ingredient
from ..exceptions.receip_exceptions import *
from app.auth.domain.user import UserId

logger = logging.getLogger(__name__)


class Recipe:
    def __init__(self):
        """Initialize Recipe with default values"""
        # Identity attributes
        self.id: Optional[RecipeId] = None
        self.name: Optional[str] = None
        self.author_id: Optional[UserId] = None
        self.description: Optional[str] = None
        self.difficulty: Optional[DifficultyLevel] = None
        self.cuisine: Optional[CuisineType] = None

        # Collections - private attributes
        self._ingredients: List[Ingredient] = []
        self._steps: List[Step] = []
        self._tags: Set[Tag] = set()
        self._meal_types: Set[MealType] = set()

        # Metadata - private attributes
        self._serving_info: Optional[ServingInfo] = None
        self._cooking_time: Optional[CookingTime] = None
        self._nutritional_info: Optional[NutritionalInfo] = None

        # Tracking - private attributes
        self._rating_sum: int = 0
        self._rating_count: int = 0
        self._view_count: int = 0
        self._favorite_count: int = 0
        self.version: int = 1

        # Timestamps - private attributes
        self._created_at: Optional[datetime] = None
        self._updated_at: Optional[datetime] = None
        self.deleted_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        name: str,
        author_id: UserId,
        description: Optional[str] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        cuisine: Optional[CuisineType] = None,
    ) -> "Recipe":
        """
        Static constructor for creating a new Recipe (Domain Event style)
        Use this when creating a brand new recipe from user input
        """
        if not name or not name.strip():
            raise RecipeValidationException("Recipe name cannot be empty", "EMPTY_NAME")

        if len(name.strip()) > 200:
            raise RecipeValidationException(
                "Recipe name cannot exceed 200 characters", "NAME_TOO_LONG"
            )

        recipe = cls.__new__(cls)

        recipe.id = RecipeId()  # Id will be set upon persistence
        recipe.name = name.strip()
        recipe.author_id = author_id
        recipe.description = description.strip() if description else None
        recipe.difficulty = difficulty
        recipe.cuisine = cuisine

        recipe._ingredients = []
        recipe._steps = []
        recipe._tags = set()

        recipe._serving_info = None
        recipe._cooking_time = None
        recipe._nutritional_info = None
        recipe._meal_types = set()

        recipe._rating_sum = 0
        recipe._rating_count = 0
        recipe._view_count = 0
        recipe._favorite_count = 0
        recipe.version = 1

        recipe._created_at = datetime.now(timezone.utc)
        recipe._updated_at = datetime.now(timezone.utc)
        recipe.deleted_at = None

        logger.info(
            f"Recipe created: {recipe.id} - '{recipe.name}' by {recipe.author_id}"
        )
        return recipe

    @classmethod
    def reconstruct(
        cls,
        id: RecipeId,
        name: str,
        author_id: UserId,
        description: Optional[str],
        difficulty: DifficultyLevel,
        cuisine: Optional[CuisineType],
        ingredients: List[Ingredient],
        steps: List[Step],
        tags: Set[Tag],
        meal_types: Set[MealType],
        serving_info: Optional[ServingInfo],
        cooking_time: Optional[CookingTime],
        nutritional_info: Optional[NutritionalInfo],
        rating_sum: int,
        rating_count: int,
        view_count: int,
        favorite_count: int,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        deleted_at: Optional[datetime],
    ) -> "Recipe":
        """
        Static constructor for reconstructing Recipe from persistence (DB/Cache)
        Use this when loading an existing recipe from database or cache
        """
        if version < 1:
            raise RecipeValidationException(
                f"Invalid version {version} for recipe {id}", "INVALID_VERSION"
            )

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        if deleted_at and deleted_at.tzinfo is None:
            deleted_at = deleted_at.replace(tzinfo=timezone.utc)

        if created_at > datetime.now(timezone.utc):
            raise RecipeValidationException(
                f"Invalid creation date for recipe {id}", "INVALID_CREATION_DATE"
            )

        # Crear instancia
        recipe = cls.__new__(cls)

        # Reconstruir estado completo
        recipe.id = id
        recipe.name = name
        recipe.author_id = author_id
        recipe.description = description
        recipe.difficulty = difficulty
        recipe.cuisine = cuisine

        # Collections
        recipe._ingredients = ingredients
        recipe._steps = steps
        recipe._tags = tags

        # Metadata
        recipe._serving_info = serving_info
        recipe._cooking_time = cooking_time
        recipe._nutritional_info = nutritional_info
        recipe._meal_types = meal_types

        # Tracking
        recipe._rating_sum = rating_sum
        recipe._rating_count = rating_count
        recipe._view_count = view_count
        recipe._favorite_count = favorite_count
        recipe.version = version

        # Timestamps
        recipe._created_at = created_at
        recipe._updated_at = updated_at
        recipe.deleted_at = deleted_at

        logger.debug(
            f"Recipe reconstructed from persistence: {recipe.id} (v{recipe.version})"
        )

        return recipe

    def _check_not_deleted(self) -> None:
        """Check if recipe is deleted before operations"""
        if self.deleted_at:
            raise RecipeDeletedException(str(self.id))

    def _record_update(self) -> None:
        """Internal method to update timestamps and log changes"""
        old_updated = self._updated_at
        self._updated_at = datetime.now(timezone.utc)
        self.version += 1

        logger.debug(
            f"Recipe {self.id} updated at {self._updated_at} (version {self.version})"
        )

    def mark_deleted(self) -> None:
        """Soft delete the recipe"""
        self.deleted_at = datetime.now(timezone.utc)
        self._record_update()
        logger.info(f"Recipe {self.id} marked as deleted")

    def restore(self) -> None:
        """Restore a soft-deleted recipe"""
        self.deleted_at = None
        self._record_update()
        logger.info(f"Recipe {self.id} restored")

    def add_ingredient(self, ingredient: Ingredient) -> None:
        self._check_not_deleted()

        if any(i.id == ingredient.id for i in self._ingredients):
            raise IngredientAlreadyExistsException(ingredient.name, str(self.id))

        self._ingredients.append(ingredient)
        self._record_update()
        logger.debug(f"Ingredient {ingredient.name} added to recipe {self.id}")

    def remove_ingredient(self, ingredient_id: IngredientId) -> None:
        self._check_not_deleted()

        initial_count = len(self._ingredients)
        self._ingredients = [i for i in self._ingredients if i.id != ingredient_id]

        if len(self._ingredients) < initial_count:
            self._record_update()
            logger.debug(f"Ingredient {ingredient_id} removed from recipe {self.id}")
        else:
            logger.warning(
                f"Attempted to remove non-existent ingredient {ingredient_id} from recipe {self.id}"
            )

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
        self._check_not_deleted()

        if not description or not description.strip():
            raise RecipeValidationException(
                "Step description cannot be empty", "EMPTY_STEP_DESCRIPTION"
            )

        step = Step(
            number=len(self._steps) + 1,
            description=description.strip(),
            duration_minutes=duration_minutes,
            technique=technique,
            temperature=temperature,
        )

        self._steps.append(step)
        self._record_update()
        logger.debug(f"Step {step.number} added to recipe {self.id}")

    def get_steps(self) -> List[Step]:
        return self._steps.copy()

    def reorder_steps(self, new_order: List[int]) -> None:
        """Reorder steps by their current indices"""
        self._check_not_deleted()

        if len(new_order) != len(self._steps):
            raise InvalidStepOrderException("New order must contain all steps")

        if set(new_order) != set(range(len(self._steps))):
            raise InvalidStepOrderException("New order contains invalid indices")

        try:
            reordered_steps = [self._steps[i] for i in new_order]
            # Renumber steps sequentially
            self._steps = [
                Step(
                    number=i + 1,
                    description=step.description,
                    duration_minutes=step.duration_minutes,
                    technique=step.technique,
                    temperature=step.temperature,
                )
                for i, step in enumerate(reordered_steps)
            ]
            self._record_update()
            logger.debug(f"Steps reordered for recipe {self.id}")
        except IndexError as e:
            logger.error(f"Error reordering steps for recipe {self.id}: {e}")
            raise InvalidStepOrderException("Invalid step indices provided") from e

    def add_tag(self, tag: Tag) -> None:
        self._check_not_deleted()
        self._tags.add(tag)
        self._record_update()
        logger.debug(f"Tag '{tag.name}' added to recipe {self.id}")

    def remove_tag(self, tag: Tag) -> None:
        self._check_not_deleted()
        self._tags.discard(tag)
        self._record_update()
        logger.debug(f"Tag '{tag.name}' removed from recipe {self.id}")

    def get_tags(self) -> Set[Tag]:
        return self._tags.copy()

    def add_meal_type(self, meal_type: MealType) -> None:
        self._check_not_deleted()
        self._meal_types.add(meal_type)
        self._record_update()
        logger.debug(f"Meal type '{meal_type}' added to recipe {self.id}")

    def get_meal_types(self) -> Set[MealType]:
        return self._meal_types.copy()

    def set_serving_info(self, serving_info: ServingInfo) -> None:
        self._check_not_deleted()
        self._serving_info = serving_info
        self._record_update()
        logger.debug(f"Serving info updated for recipe {self.id}")

    def get_serving_info(self) -> Optional[ServingInfo]:
        return self._serving_info

    def set_cooking_time(self, cooking_time: CookingTime) -> None:
        self._check_not_deleted()
        self._cooking_time = cooking_time
        self._record_update()
        logger.debug(f"Cooking time updated for recipe {self.id}")

    def get_cooking_time(self) -> Optional[CookingTime]:
        return self._cooking_time

    def calculate_total_time(self) -> int:
        """Calculate total time including prep and cooking"""
        self._check_not_deleted()

        if self._cooking_time:
            return self._cooking_time.total_minutes

        # Fallback to sum of step durations
        total = sum(s.duration_minutes for s in self._steps if s.duration_minutes)
        logger.debug(f"Calculated total time for recipe {self.id}: {total} minutes")
        return total

    def set_nutritional_info(self, nutritional_info: NutritionalInfo) -> None:
        self._check_not_deleted()
        self._nutritional_info = nutritional_info
        self._record_update()
        logger.debug(f"Nutritional info updated for recipe {self.id}")

    def get_nutritional_info(self) -> Optional[NutritionalInfo]:
        return self._nutritional_info

    def get_nutritional_info_per_serving(self) -> Optional[NutritionalInfo]:
        """Get nutritional info scaled to one serving"""
        self._check_not_deleted()

        if not self._nutritional_info or not self._serving_info:
            logger.debug(
                f"No nutritional info or serving info available for recipe {self.id}"
            )
            return None

        try:
            factor = Decimal(1) / Decimal(self._serving_info.servings)
            scaled_info = self._nutritional_info.scale(factor)
            logger.debug(
                f"Calculated nutritional info per serving for recipe {self.id}"
            )
            return scaled_info
        except (InvalidOperation, ZeroDivisionError) as e:
            logger.error(f"Error scaling nutritional info for recipe {self.id}: {e}")
            raise InvalidQuantityException(
                "Invalid serving size for nutritional scaling"
            ) from e

    def is_suitable_for_diet(self, diet: DietType) -> bool:
        """Check if recipe is suitable for a specific diet"""
        self._check_not_deleted()
        suitable = all(
            ingredient.is_suitable_for(diet) for ingredient in self._ingredients
        )
        logger.debug(
            f"Diet suitability check for {diet} in recipe {self.id}: {suitable}"
        )
        return suitable

    def get_compatible_diets(self) -> Set[DietType]:
        """Get all diets this recipe is compatible with"""
        self._check_not_deleted()
        compatible_diets = {
            diet for diet in DietType if self.is_suitable_for_diet(diet)
        }
        logger.debug(f"Compatible diets for recipe {self.id}: {compatible_diets}")
        return compatible_diets

    def get_allergens(self) -> Set[str]:
        """Get a set of all allergens present in the recipe"""
        self._check_not_deleted()
        allergens: Set[str] = set()
        for ingredient in self._ingredients:
            allergens.update(ingredient.properties.allergens)

        logger.debug(f"Allergens detected in recipe {self.id}: {allergens}")
        return allergens

    def add_rating(self, rating: int) -> None:
        """Add a rating to the recipe (1-5 scale)"""
        self._check_not_deleted()

        if not 1 <= rating <= 5:
            raise RecipeValidationException(
                "Rating must be between 1 and 5", "INVALID_RATING"
            )

        self._rating_sum += rating
        self._rating_count += 1
        self._record_update()
        logger.debug(f"Rating {rating} added to recipe {self.id}")

    def get_average_rating(self) -> Optional[float]:
        """Get the average rating"""
        if self._rating_count == 0:
            return None
        return round(self._rating_sum / self._rating_count, 2)

    def increment_view_count(self) -> None:
        self._view_count += 1
        # No record update for view counts to avoid version spam
        logger.debug(f"View count incremented for recipe {self.id}")

    def get_view_count(self) -> int:
        return self._view_count

    def increment_favorite_count(self) -> None:
        self._favorite_count += 1
        self._record_update()
        logger.debug(f"Favorite count incremented for recipe {self.id}")

    def get_favorite_count(self) -> int:
        return self._favorite_count

    def get_created_at(self) -> Optional[datetime]:
        return self._created_at

    def get_updated_at(self) -> Optional[datetime]:
        return self._updated_at

    def __repr__(self) -> str:
        return f"Recipe(id={self.id}, name='{self.name}', author={self.author_id}, version={self.version})"

    def __str__(self) -> str:
        difficulty_str = self.difficulty.value if self.difficulty else "Unknown"
        return f"'{self.name}' by {self.author_id} ({difficulty_str})"
