from datetime import datetime
from typing import List, Optional, Set
import logging
from typing import Optional, Set, List
from datetime import datetime
from ...exceptions import *
from app.modules.auth.domain.user import UserId
from ..value_objects.value_objects_standard import *
from ..value_objects.enums import DifficultyLevel, CuisineType, MealType, DietType
from ..entities.ingredient import Ingredient
from typing import TypedDict


class RecipeReconstructData(TypedDict):
    """Estructura tipada para reconstrucción de Recipe"""

    # Información básica
    id: RecipeId
    name: str
    author_id: UserId
    description: str
    difficulty: DifficultyLevel
    cuisine: CuisineType

    # Colecciones
    ingredients: List[Ingredient]
    steps: List[Step]
    tags: Set[Tag]
    meal_types: Set[MealType]

    # Metadata
    serving_info: ServingInfo
    cooking_time: CookingTime
    nutritional_info: Optional[NutritionalInfo]

    # Tracking
    rating_sum: int
    review_count: int
    view_count: int
    favorite_count: int
    version: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


@dataclass
class RecipeCreateBasicInfo:
    """
    Información básica para crear una receta.
    Se auto-valida al ser creada.
    """

    name: str
    author_id: UserId
    description: Optional[str]
    difficulty: DifficultyLevel
    cuisine: CuisineType

    def __post_init__(self):
        """Validación automática después de inicialización"""
        self._validate()

    def _validate(self) -> None:
        """Valida todos los campos"""
        self._validate_name()
        self._validate_difficulty()
        self._validate_cuisine()
        self._validate_author_id()

    def _validate_name(self) -> None:
        """Valida el nombre"""
        if not self.name or not self.name.strip():
            raise RecipeValidationException("Recipe name cannot be empty", "EMPTY_NAME")

        if len(self.name.strip()) > 200:
            raise RecipeValidationException(
                "Recipe name cannot exceed 200 characters", "NAME_TOO_LONG"
            )

    def _validate_description(self) -> None:
        """Valida la descripción"""
        if self.description:
            if len(self.description.strip()) < 10:
                raise RecipeValidationException(
                    "Recipe description must be at least 10 characters",
                    "DESCRIPTION_TOO_SHORT",
                )

            if len(self.description.strip()) > 255:
                raise RecipeValidationException(
                    "Recipe description cannot exceed 255 characters",
                    "DESCRIPTION_TOO_LONG",
                )

    def _validate_difficulty(self) -> None:
        """Valida la dificultad"""
        if not self.difficulty.is_valid():
            raise RecipeValidationException(
                "Invalid difficulty level specified", "INVALID_DIFFICULTY"
            )

    def _validate_cuisine(self) -> None:
        """Valida el tipo de cocina"""
        if not self.cuisine.is_valid():
            raise RecipeValidationException(
                "Invalid cuisine type specified", "INVALID_CUISINE"
            )

    def _validate_author_id(self) -> None:
        """Valida el ID del autor"""
        if self.author_id is None:
            raise RecipeValidationException(
                "Author ID must be provided", "MISSING_AUTHOR_ID"
            )


@dataclass
class RecipeCreateContent:
    """
    Contenido de la receta (ingredientes, pasos, tags).
    Se auto-valida al ser creada.
    """

    ingredients: List[Ingredient]
    steps: List[Step]
    tags: Set[Tag]

    def __post_init__(self):
        """Validación automática después de inicialización"""
        self._validate()

    def _validate(self) -> None:
        """Valida todos los campos"""
        if not self.ingredients or len(self.ingredients) == 0:
            raise RecipeValidationException(
                "At least one ingredient must be specified", "NO_INGREDIENTS"
            )

        if not self.steps or len(self.steps) == 0:
            raise RecipeValidationException(
                "At least one step must be specified", "NO_STEPS"
            )

        if not self.tags or len(self.tags) == 0:
            raise RecipeValidationException(
                "At least one tag must be specified", "NO_TAGS"
            )


@dataclass
class RecipeCreateDetails:
    """
    Detalles adicionales de la receta.
    Se auto-valida al ser creada.
    """

    meal_types: Set[MealType]
    serving_info: ServingInfo
    cooking_time: CookingTime
    nutritional_info: Optional[NutritionalInfo] = None

    def __post_init__(self):
        """Validación automática después de inicialización"""
        self._validate()

    def _validate(self) -> None:
        """Valida todos los campos"""
        if not self.meal_types or len(self.meal_types) == 0:
            raise RecipeValidationException(
                "At least one meal type must be specified", "NO_MEAL_TYPES"
            )

        if self.serving_info is None:
            raise RecipeValidationException(
                "Serving info must be provided", "MISSING_SERVING_INFO"
            )

        if self.cooking_time is None:
            raise RecipeValidationException(
                "Cooking time must be provided", "MISSING_COOKING_TIME"
            )
