import logging
from dataclasses import dataclass, field
from typing import Optional, List, Set, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from ..value_objects.value_objects_standard import (
    CookingTime,
    NutritionalInfo,
    ServingInfo,
    Step,
    Tag,
)
from .enums import MealType
from ..entities.ingredient import Ingredient, IngredientId
from ..entities.recipe import RecipeId


logger = logging.getLogger("app.modules.recipe")


class TimeStamps:
    """Value Object for entity timestamps."""

    def __init__(
        self,
        created_at: datetime,
        updated_at: datetime,
        deleted_at: Optional[datetime] = None,
    ):
        self._created_at = self._ensure_timezone(created_at)
        self._updated_at = self._ensure_timezone(updated_at)
        self._deleted_at = self._ensure_timezone(deleted_at) if deleted_at else None

        self._validate_timestamps()

    def _ensure_timezone(self, dt: datetime) -> datetime:
        """Asegurar que el datetime tenga timezone."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _validate_timestamps(self):
        """Validar la consistencia de los timestamps."""
        now = datetime.now(timezone.utc)

        if self._created_at > now:
            raise ValueError("Creation date cannot be in the future")

        time_diff = (self._created_at - self._updated_at).total_seconds()
        if time_diff > 1:
            raise ValueError(
                f"Update date cannot be before creation date (diff: {time_diff}s)"
            )

        if self._deleted_at and self._deleted_at < self._created_at:
            raise ValueError("Deletion date cannot be before creation date")

    @classmethod
    def create(cls) -> "TimeStamps":
        """Crear nuevos timestamps para una entidad nueva."""
        now = datetime.now(timezone.utc)
        return cls(created_at=now, updated_at=now)

    @classmethod
    def reconstruct(
        cls,
        created_at: datetime,
        updated_at: datetime,
        deleted_at: Optional[datetime] = None,
    ) -> "TimeStamps":
        """Reconstruir desde persistencia."""
        entity = cls(created_at, updated_at, deleted_at)
        entity._ensure_timezone(created_at)
        entity._ensure_timezone(updated_at)
        if deleted_at:
            entity._ensure_timezone(deleted_at)

        return entity

    def record_update(self) -> "TimeStamps":
        """Registrar una actualización."""
        return TimeStamps(
            created_at=self._created_at,
            updated_at=datetime.now(timezone.utc),
            deleted_at=self._deleted_at,
        )

    def mark_deleted(self) -> "TimeStamps":
        """Marcar como eliminado."""
        return TimeStamps(
            created_at=self._created_at,
            updated_at=datetime.now(timezone.utc),
            deleted_at=datetime.now(timezone.utc),
        )

    def mark_restored(self) -> "TimeStamps":
        """Restaurar eliminación."""
        return TimeStamps(
            created_at=self._created_at,
            updated_at=datetime.now(timezone.utc),
            deleted_at=None,
        )

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def deleted_at(self) -> Optional[datetime]:
        return self._deleted_at

    def is_deleted(self) -> bool:
        return self._deleted_at is not None

    def __eq__(self, other):
        if not isinstance(other, TimeStamps):
            return False
        return (
            self._created_at == other._created_at
            and self._updated_at == other._updated_at
            and self._deleted_at == other._deleted_at
        )


class RecipeCollections:
    """Value Object compuesto para colecciones de la receta."""

    def __init__(
        self,
        ingredients: List["Ingredient"] = [],
        steps: List[Step] = [],
        tags: Set[Tag] = set(),
        meal_types: Set[MealType] = set(),
    ):
        self._ingredients = ingredients or []
        self._steps = steps or []
        self._tags = tags or set()
        self._meal_types = meal_types or set()

    def add_ingredient(self, ingredient: "Ingredient") -> "RecipeCollections":
        """Agregar ingrediente."""
        if any(i.name.lower() == ingredient.name.lower() for i in self._ingredients):
            raise ValueError(
                f"Ingredient with name '{ingredient.name}' already exists in recipe"
            )

        new_ingredients = self._ingredients.copy()
        new_ingredients.append(ingredient)

        return RecipeCollections.reconstruct(
            new_ingredients, self._steps, self._tags, self._meal_types
        )

    def add_ingredients(self, ingredients: List["Ingredient"]) -> "RecipeCollections":
        """Agregar múltiples ingredientes."""
        new_ingredients = self._ingredients.copy()

        for ingredient in ingredients:
            if any(i.name.lower() == ingredient.name.lower() for i in new_ingredients):
                raise ValueError(
                    f"Ingredient with name '{ingredient.name}' already exists in recipe"
                )
            new_ingredients.append(ingredient)

        return RecipeCollections.reconstruct(
            new_ingredients, self._steps, self._tags, self._meal_types
        )

    def clear_ingredients(self) -> "RecipeCollections":
        """Remover todos los ingredientes."""
        return RecipeCollections.reconstruct(
            ingredients=[],
            steps=self._steps,
            tags=self._tags,
            meal_types=self._meal_types,
        )

    def remove_ingredient(self, ingredient_id: IngredientId) -> "RecipeCollections":
        """Remover ingrediente."""
        new_ingredients = [i for i in self._ingredients if i.id != ingredient_id]
        return RecipeCollections.reconstruct(
            ingredients=new_ingredients,
            steps=self._steps,
            tags=self._tags,
            meal_types=self._meal_types,
        )

    def add_step(self, step: Step) -> "RecipeCollections":
        """Agregar paso."""
        # Verificar número único
        if any(s.number == step.number for s in self._steps):
            raise ValueError(f"Step number {step.number} already exists")

        new_steps = self._steps + [step]
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=new_steps,
            tags=self._tags,
            meal_types=self._meal_types,
        )

    def add_steps(self, steps: List[Step]) -> "RecipeCollections":
        """Agregar múltiples pasos."""
        new_steps = self._steps.copy()

        for step in steps:
            if any(s.number == step.number for s in new_steps):
                raise ValueError(f"Step number {step.number} already exists")
            new_steps.append(step)

        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=new_steps,
            tags=self._tags,
            meal_types=self._meal_types,
        )

    def clear_steps(self) -> "RecipeCollections":
        """Remover todos los pasos."""
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=[],
            tags=self._tags,
            meal_types=self._meal_types,
        )

    def add_tag(self, tag: Tag) -> "RecipeCollections":
        """Agregar etiqueta."""
        new_tags = self._tags | {tag}
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=new_tags,
            meal_types=self._meal_types,
        )

    def add_tags(self, tags: Set[Tag]) -> "RecipeCollections":
        """Agregar múltiples etiquetas."""
        new_tags = self._tags | tags
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=new_tags,
            meal_types=self._meal_types,
        )

    def add_meal_types(self, meal_types: Set[MealType]) -> "RecipeCollections":
        """Agregar tipos de comida."""
        new_meal_types = self._meal_types | meal_types
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=self._tags,
            meal_types=new_meal_types,
        )

    def clear_meal_types(self) -> "RecipeCollections":
        """Remover todos los tipos de comida."""
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=self._tags,
            meal_types=set(),
        )

    def add_meal_type(self, meal_type: MealType) -> "RecipeCollections":
        """Agregar tipo de comida."""
        new_meal_types = self._meal_types | {meal_type}
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=self._tags,
            meal_types=new_meal_types,
        )

    def clear_tags(self) -> "RecipeCollections":
        """Remover todas las etiquetas."""
        return RecipeCollections.reconstruct(
            ingredients=self._ingredients,
            steps=self._steps,
            tags=set(),
            meal_types=self._meal_types,
        )

    @property
    def ingredients(self) -> List["Ingredient"]:
        return self._ingredients.copy()

    @property
    def steps(self) -> List[Step]:
        return self._steps.copy()

    @property
    def tags(self) -> Set[Tag]:
        return self._tags.copy()

    @property
    def meal_types(self) -> Set[MealType]:
        return self._meal_types.copy()

    @classmethod
    def reconstruct(
        cls,
        ingredients: List["Ingredient"],
        steps: List[Step],
        tags: Set[Tag],
        meal_types: Set[MealType],
    ) -> "RecipeCollections":
        return cls(ingredients, steps, tags, meal_types)

    def __eq__(self, other):
        if not isinstance(other, RecipeCollections):
            return False
        return (
            self._ingredients == other._ingredients
            and self._steps == other._steps
            and self._tags == other._tags
            and self._meal_types == other._meal_types
        )


class RecipeTrackingInfo:
    """Value Object compuesto para información de tracking."""

    def __init__(
        self,
        rating_sum: int = 0,
        rating_count: int = 0,
        view_count: int = 0,
        favorite_count: int = 0,
        version: int = 1,
    ):
        if rating_sum < 0 or rating_count < 0 or view_count < 0 or favorite_count < 0:
            raise ValueError("Count values cannot be negative")
        if version < 1:
            raise ValueError("Version must be at least 1")

        self._rating_sum = rating_sum
        self._rating_count = rating_count
        self._view_count = view_count
        self._favorite_count = favorite_count
        self._version = version

    def add_rating(self, rating: int) -> "RecipeTrackingInfo":
        """Agregar rating."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        return RecipeTrackingInfo(
            rating_sum=self._rating_sum + rating,
            rating_count=self._rating_count + 1,
            view_count=self._view_count,
            favorite_count=self._favorite_count,
            version=self._version,
        )

    def increment_view_count(self) -> "RecipeTrackingInfo":
        """Incrementar contador de vistas."""
        return RecipeTrackingInfo(
            rating_sum=self._rating_sum,
            rating_count=self._rating_count,
            view_count=self._view_count + 1,
            favorite_count=self._favorite_count,
            version=self._version,
        )

    def increment_favorite_count(self) -> "RecipeTrackingInfo":
        """Incrementar contador de favoritos."""
        return RecipeTrackingInfo(
            rating_sum=self._rating_sum,
            rating_count=self._rating_count,
            view_count=self._view_count,
            favorite_count=self._favorite_count + 1,
            version=self._version,
        )

    def decrement_favorite_count(self) -> "RecipeTrackingInfo":
        """Decrementar contador de favoritos."""
        if self._favorite_count == 0:
            raise ValueError("Favorite count cannot be negative")
        return RecipeTrackingInfo(
            rating_sum=self._rating_sum,
            rating_count=self._rating_count,
            view_count=self._view_count,
            favorite_count=self._favorite_count - 1,
            version=self._version,
        )

    def increase_version(self) -> "RecipeTrackingInfo":
        """Incrementar versión."""
        return RecipeTrackingInfo(
            rating_sum=self._rating_sum,
            rating_count=self._rating_count,
            view_count=self._view_count,
            favorite_count=self._favorite_count,
            version=self._version + 1,
        )

    def calculate_average_rating(self) -> Optional[float]:
        """Calcular rating promedio."""
        if self._rating_count == 0:
            return None
        return round(self._rating_sum / self._rating_count, 2)

    @property
    def rating_sum(self) -> int:
        return self._rating_sum

    @property
    def rating_count(self) -> int:
        return self._rating_count

    @property
    def view_count(self) -> int:
        return self._view_count

    @property
    def favorite_count(self) -> int:
        return self._favorite_count

    @property
    def version(self) -> int:
        return self._version

    @classmethod
    def reconstruct(
        cls,
        rating_sum: int,
        rating_count: int,
        view_count: int,
        favorite_count: int,
        version: int,
    ) -> "RecipeTrackingInfo":
        return cls(rating_sum, rating_count, view_count, favorite_count, version)

    def __eq__(self, other):
        if not isinstance(other, RecipeTrackingInfo):
            return False
        return (
            self._rating_sum == other._rating_sum
            and self._rating_count == other._rating_count
            and self._view_count == other._view_count
            and self._favorite_count == other._favorite_count
            and self._version == other._version
        )


class RecipeMetadata:
    """Value Object compuesto para metadata de la receta."""

    def __init__(
        self,
        cooking_time: Optional[CookingTime] = None,
        nutritional_info: Optional[NutritionalInfo] = None,
        serving_info: Optional[ServingInfo] = None,
    ):
        self._cooking_time = cooking_time
        self._nutritional_info = nutritional_info
        self._serving_info = serving_info

    def update_cooking_time(self, cooking_time: CookingTime) -> "RecipeMetadata":
        """Actualizar tiempo de cocción."""
        return RecipeMetadata(
            cooking_time=cooking_time,
            nutritional_info=self._nutritional_info,
            serving_info=self._serving_info,
        )

    def update_nutritional_info(
        self, nutritional_info: NutritionalInfo
    ) -> "RecipeMetadata":
        """Actualizar información nutricional."""
        return RecipeMetadata(
            cooking_time=self._cooking_time,
            nutritional_info=nutritional_info,
            serving_info=self._serving_info,
        )

    def update_serving_info(self, serving_info: ServingInfo) -> "RecipeMetadata":
        """Actualizar información de porciones."""
        return RecipeMetadata(
            cooking_time=self._cooking_time,
            nutritional_info=self._nutritional_info,
            serving_info=serving_info,
        )

    def calculate_nutritional_info_per_serving(self) -> Optional[NutritionalInfo]:
        """Calcular información nutricional por porción."""
        if not self._nutritional_info or not self._serving_info:
            return None

        try:
            factor = Decimal(1) / Decimal(self._serving_info.servings)
            return self._nutritional_info.scale(factor)
        except (InvalidOperation, ZeroDivisionError) as e:
            logger.error(f"Error scaling nutritional info: {e}")
            raise ValueError("Invalid serving size for nutritional scaling") from e

    @property
    def cooking_time(self) -> Optional[CookingTime]:
        return self._cooking_time

    @property
    def nutritional_info(self) -> Optional[NutritionalInfo]:
        return self._nutritional_info

    @property
    def serving_info(self) -> Optional[ServingInfo]:
        return self._serving_info

    @classmethod
    def reconstruct(
        cls,
        cooking_time: Optional[CookingTime],
        nutritional_info: Optional[NutritionalInfo],
        serving_info: Optional[ServingInfo],
    ) -> "RecipeMetadata":
        return cls(cooking_time, nutritional_info, serving_info)

    def __eq__(self, other):
        if not isinstance(other, RecipeMetadata):
            return False
        return (
            self._cooking_time == other._cooking_time
            and self._nutritional_info == other._nutritional_info
            and self._serving_info == other._serving_info
        )
