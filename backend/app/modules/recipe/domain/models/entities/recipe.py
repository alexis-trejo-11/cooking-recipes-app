import logging
from typing import Optional, Set, List
from datetime import datetime
from app.modules.auth.domain.user import UserId
from ...exceptions import *
from ..value_objects.param_dtos import *
from ..value_objects.value_objects_standard import *
from ..value_objects.enums import DifficultyLevel, CuisineType, MealType, DietType
from ..value_objects.value_objects_compound import (
    RecipeCollections,
    RecipeTrackingInfo,
    RecipeMetadata,
    TimeStamps,
    TimeStamps,
)
from .ingredient import Ingredient


logger = logging.getLogger(__name__)


class Recipe:
    """
    Entidad principal Recipe que representa una receta en el dominio.

    Esta entidad utiliza Value Objects para evitar primitive obsession
    y mantiene la lógica de negocio dentro de los objetos de valor apropiados.
    """

    def __init__(self):
        """Inicializar Recipe con valores por defecto."""
        self._id: RecipeId = RecipeId()
        self._name: str = ""
        self._description: Optional[str] = None
        self._image_url: Optional[str] = None
        self._author_id: UserId = UserId.zero()
        self._difficulty: DifficultyLevel = DifficultyLevel.UNKNOWN
        self._cuisine: CuisineType = CuisineType.UNKNOWN
        self._collections: RecipeCollections = RecipeCollections()
        self._tracking_info: RecipeTrackingInfo = RecipeTrackingInfo()
        self._metadata: RecipeMetadata = RecipeMetadata()
        self._timestamps: TimeStamps = TimeStamps.create()

    @classmethod
    def create(
        cls,
        basic_info: RecipeCreateBasicInfo,
        content: RecipeCreateContent,
        details: RecipeCreateDetails,
    ) -> "Recipe":
        """
        Constructor estático para crear una nueva Recipe.

        Args:
            basic_info: Información básica (nombre, autor, descripción, etc.)
            content: Contenido (ingredientes, pasos, tags)
            details: Detalles (meal types, serving info, cooking time)

        Returns:
            Recipe: Nueva instancia de Recipe

        Raises:
            RecipeValidationException: Si la validación falla
        """
        # Validaciones de información básica
        recipe = cls()

        recipe._id = RecipeId.generate()
        recipe._name = basic_info.name.strip()
        recipe._author_id = basic_info.author_id
        recipe._description = basic_info.description
        recipe._difficulty = basic_info.difficulty
        recipe._cuisine = basic_info.cuisine

        recipe._collections = recipe._collections.add_meal_types(details.meal_types)
        recipe._collections = recipe._collections.add_ingredients(content.ingredients)
        recipe._collections = recipe._collections.add_steps(content.steps)
        recipe._collections = recipe._collections.add_tags(content.tags)

        recipe._metadata = recipe._metadata.update_serving_info(details.serving_info)
        recipe._metadata = recipe._metadata.update_cooking_time(details.cooking_time)

        if details.nutritional_info:
            recipe._metadata = recipe._metadata.update_nutritional_info(
                details.nutritional_info
            )

        recipe._timestamps = TimeStamps.create()
        logger.info(
            f"Recipe created: {recipe.id} - '{recipe.name}' by {recipe.author_id}"
        )
        return recipe

    @classmethod
    def reconstruct(cls, data: RecipeReconstructData) -> "Recipe":
        """
        Reconstruir Recipe desde persistencia.

        NO hace validaciones porque los datos vienen de la DB
        y ya fueron validados al momento de crear/actualizar.

        Args:
            data: Todos los datos necesarios para reconstruir

        Returns:
            Recipe: Instancia reconstruida
        """
        recipe = cls()

        # Información básica
        recipe._id = data["id"]
        recipe._name = data["name"]
        recipe._author_id = data["author_id"]
        recipe._description = data["description"]
        recipe._difficulty = data["difficulty"]
        recipe._cuisine = data["cuisine"]

        # Value Objects compuestos
        recipe._collections = RecipeCollections.reconstruct(
            ingredients=data["ingredients"],
            steps=data["steps"],
            tags=data["tags"],
            meal_types=data["meal_types"],
        )

        recipe._metadata = RecipeMetadata.reconstruct(
            cooking_time=data["cooking_time"],
            nutritional_info=data["nutritional_info"],
            serving_info=data["serving_info"],
        )

        recipe._tracking_info = RecipeTrackingInfo.reconstruct(
            rating_sum=data["rating_sum"],
            review_count=data["review_count"],
            view_count=data["view_count"],
            favorite_count=data["favorite_count"],
            version=data["version"],
        )

        recipe._timestamps = TimeStamps.reconstruct(
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            deleted_at=data["deleted_at"],
        )

        logger.debug(f"Recipe reconstructed: {recipe.id} (v{recipe.version})")
        return recipe

    def _check_not_deleted(self) -> None:
        """Verificar que la receta no esté eliminada."""
        if self.is_deleted:
            raise RecipeDeletedException(
                f"Recipe {self.id} is deleted and cannot be modified"
            )

    def _record_update(self) -> None:
        """Registrar una actualización."""
        old_version = self.version
        self._timestamps = self._timestamps.record_update()

        logger.debug(
            f"Recipe {self.id} updated from v{old_version} to v{self.version} "
            f"at {self.updated_at}"
        )

    def soft_delete(self) -> None:
        """Eliminación lógica de la receta."""
        self._check_not_deleted()
        self._timestamps = self._timestamps.mark_deleted()
        self._record_update()
        logger.info(f"Recipe {self.id} marked as deleted")

    def restore(self) -> None:
        """Restaurar receta eliminada."""
        if not self.is_deleted:
            raise RecipeValidationException(
                f"Recipe {self.id} is not deleted and cannot be restored", "NOT_DELETED"
            )

        self._timestamps = self._timestamps.mark_restored()
        self._record_update()
        logger.info(f"Recipe {self.id} restored")

    def update_basic_info(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        difficulty: Optional[DifficultyLevel] = None,
        cuisine: Optional[CuisineType] = None,
    ) -> None:
        """Actualizar información básica de la receta."""
        self._check_not_deleted()
        changed = False

        if name is not None:
            if not name or not name.strip():
                raise RecipeValidationException(
                    "Recipe name cannot be empty", "EMPTY_NAME"
                )
            if len(name.strip()) > 200:
                raise RecipeValidationException(
                    "Recipe name cannot exceed 200 characters", "NAME_TOO_LONG"
                )
            self._name = name.strip()
            changed = True
            logger.debug(f"Recipe {self.id} name updated to '{self.name}'")

        if description is not None:
            self._description = description.strip()
            changed = True
            logger.debug(f"Recipe {self.id} description updated")

        if difficulty is not None:
            self._difficulty = difficulty
            changed = True
            logger.debug(f"Recipe {self.id} difficulty updated to {self.difficulty}")

        if cuisine is not None:
            self._cuisine = cuisine
            changed = True
            logger.debug(f"Recipe {self.id} cuisine updated to {self.cuisine}")

        if changed:
            self._record_update()

    def add_ingredient(self, ingredient: Ingredient) -> None:
        """Agregar ingrediente a la receta."""
        self._check_not_deleted()
        self._collections = self._collections.add_ingredient(ingredient)
        self._record_update()
        logger.debug(f"Ingredient {ingredient.name} added to recipe {self.id}")

    def add_ingredients(self, ingredients: List[Ingredient]) -> None:
        """Agregar múltiples ingredientes a la receta."""
        self._check_not_deleted()
        for ingredient in ingredients:
            self._collections = self._collections.add_ingredient(ingredient)
        self._record_update()
        logger.debug(f"{len(ingredients)} ingredients added to recipe {self.id}")

    def update_ingredients(self, ingredients: List[Ingredient]) -> None:
        """Actualizar lista completa de ingredientes."""
        self._check_not_deleted()

        self.clear_ingredients()
        self.add_ingredients(ingredients)

        self._record_update()
        logger.debug(f"Ingredients updated for recipe {self.id}")

    def clear_ingredients(self) -> None:
        """Remover todos los ingredientes de la receta."""
        self._check_not_deleted()
        self._collections = self._collections.clear_ingredients()
        self._record_update()
        logger.debug(f"All ingredients cleared from recipe {self.id}")

    def add_step(self, step: Step) -> None:
        """Agregar paso a la receta."""
        self._check_not_deleted()
        self._collections = self._collections.add_step(step)
        self._record_update()
        logger.debug(f"Step {step.number} added to recipe {self.id}")

    def add_steps(self, steps: List[Step]) -> None:
        """Agregar múltiples pasos a la receta."""
        self._check_not_deleted()
        for step in steps:
            self._collections = self._collections.add_step(step)
        self._record_update()
        logger.debug(f"{len(steps)} steps added to recipe {self.id}")

    def clear_steps(self) -> None:
        """Remover todos los pasos de la receta."""
        self._check_not_deleted()
        self._collections = self._collections.clear_steps()
        self._record_update()
        logger.debug(f"All steps cleared from recipe {self.id}")

    def update_steps(self, steps: List[Step]) -> None:
        """Actualizar lista completa de pasos."""
        self._check_not_deleted()

        self._collections = self._collections.clear_steps()
        self.add_steps(steps)

        self._record_update()
        logger.debug(f"Steps updated for recipe {self.id}")

    def add_tag(self, tag: Tag) -> None:
        """Agregar etiqueta a la receta."""
        self._check_not_deleted()
        self._collections = self._collections.add_tag(tag)
        self._record_update()
        logger.debug(f"Tag '{tag.name}' added to recipe {self.id}")

    def add_tags(self, tags: Set[Tag]) -> None:
        """Agregar múltiples etiquetas a la receta."""
        self._check_not_deleted()
        for tag in tags:
            self._collections = self._collections.add_tag(tag)
        self._record_update()
        logger.debug(f"{len(tags)} tags added to recipe {self.id}")

    def update_tags(self, tags: Set[Tag]) -> None:
        """Actualizar conjunto completo de etiquetas."""
        self._check_not_deleted()

        self._collections.clear_tags()
        self.add_tags(tags)

        self._record_update()
        logger.debug(f"Tags updated for recipe {self.id}")

    def clear_tags(self) -> None:
        """Remover todas las etiquetas de la receta."""
        self._check_not_deleted()
        self._collections = self._collections.clear_tags()
        self._record_update()
        logger.debug(f"All tags cleared from recipe {self.id}")

    def add_meal_type(self, meal_type: MealType) -> None:
        """Agregar tipo de comida a la receta."""
        self._check_not_deleted()
        self._collections = self._collections.add_meal_type(meal_type)
        self._record_update()
        logger.debug(f"Meal type '{meal_type}' added to recipe {self.id}")

    def add_meal_types(self, meal_types: Set[MealType]) -> None:
        """Agregar múltiples tipos de comida a la receta."""
        self._check_not_deleted()
        for meal_type in meal_types:
            self._collections = self._collections.add_meal_type(meal_type)
        self._record_update()
        logger.debug(f"{len(meal_types)} meal types added to recipe {self.id}")

    def update_meal_types(self, meal_types: Set[MealType]) -> None:
        """Actualizar conjunto completo de tipos de comida."""
        self._check_not_deleted()

        self._collections.clear_meal_types()
        self.add_meal_types(meal_types)

        self._record_update()
        logger.debug(f"Meal types updated for recipe {self.id}")

    def clear_meal_types(self) -> None:
        """Remover todos los tipos de comida de la receta."""
        self._check_not_deleted()
        self._collections = self._collections.clear_meal_types()
        self._record_update()
        logger.debug(f"All meal types cleared from recipe {self.id}")

    def update_serving_info(self, serving_info: ServingInfo) -> None:
        """Actualizar información de porciones."""
        self._check_not_deleted()
        self._metadata = self._metadata.update_serving_info(serving_info)
        self._record_update()
        logger.debug(f"Serving info updated for recipe {self.id}")

    def update_cooking_time(self, cooking_time: CookingTime) -> None:
        """Actualizar tiempo de cocción."""
        self._check_not_deleted()
        self._metadata = self._metadata.update_cooking_time(cooking_time)
        self._record_update()
        logger.debug(f"Cooking time updated for recipe {self.id}")

    def update_nutritional_info(self, nutritional_info: NutritionalInfo) -> None:
        """Actualizar información nutricional."""
        self._check_not_deleted()
        self._metadata = self._metadata.update_nutritional_info(nutritional_info)
        self._record_update()
        logger.debug(f"Nutritional info updated for recipe {self.id}")

    def calculate_total_time(self) -> int:
        """Calcular tiempo total incluyendo preparación y cocción."""
        self._check_not_deleted()

        if self.cooking_time:
            return self.cooking_time.calculate_total_minutes()

        # Fallback a suma de duraciones de pasos
        total = sum(
            step.duration_minutes for step in self.steps if step.duration_minutes
        )
        logger.debug(f"Calculated total time for recipe {self.id}: {total} minutes")
        return total

    def get_nutritional_info_per_serving(self) -> Optional[NutritionalInfo]:
        """Obtener información nutricional escalada a una porción."""
        self._check_not_deleted()
        return self._metadata.calculate_nutritional_info_per_serving()

    def is_suitable_for_diet(self, diet: DietType) -> bool:
        """Verificar si la receta es adecuada para una dieta específica."""
        self._check_not_deleted()
        suitable = all(
            ingredient.is_suitable_for(diet) for ingredient in self.ingredients
        )
        logger.debug(
            f"Diet suitability check for {diet} in recipe {self.id}: {suitable}"
        )
        return suitable

    def decrease_favorite_count(self) -> None:
        """Decrementar contador de favoritos."""
        self._check_not_deleted()
        self._tracking_info = self._tracking_info.decrement_favorite_count()
        self._record_update()
        logger.debug(f"Favorite count decremented for recipe {self.id}")

    def get_compatible_diets(self) -> Set[DietType]:
        """Obtener todas las dietas con las que esta receta es compatible."""
        self._check_not_deleted()
        compatible_diets = {
            diet for diet in DietType if self.is_suitable_for_diet(diet)
        }
        logger.debug(f"Compatible diets for recipe {self.id}: {compatible_diets}")
        return compatible_diets

    def get_allergens(self) -> Set[str]:
        """Obtener conjunto de todos los alérgenos presentes en la receta."""
        self._check_not_deleted()
        allergens: Set[str] = set()
        for ingredient in self.ingredients:
            allergens.update(ingredient.properties.allergens)

        logger.debug(f"Allergens detected in recipe {self.id}: {allergens}")
        return allergens

    @property
    def id(self) -> RecipeId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def author_id(self) -> UserId:
        return self._author_id

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def difficulty(self) -> DifficultyLevel:
        return self._difficulty

    @property
    def cuisine(self) -> CuisineType:
        return self._cuisine

    @property
    def ingredients(self) -> List[Ingredient]:
        return self._collections.ingredients

    @property
    def steps(self) -> List[Step]:
        return self._collections.steps

    @property
    def tags(self) -> Set[Tag]:
        return self._collections.tags

    @property
    def meal_types(self) -> Set[MealType]:
        return self._collections.meal_types

    @property
    def serving_info(self) -> Optional[ServingInfo]:
        return self._metadata.serving_info

    @property
    def cooking_time(self) -> Optional[CookingTime]:
        return self._metadata.cooking_time

    @property
    def nutritional_info(self) -> Optional[NutritionalInfo]:
        return self._metadata.nutritional_info

    @property
    def average_rating(self) -> Optional[float]:
        return self._tracking_info.calculate_average_rating()

    @property
    def rating_sum(self) -> int:
        return self._tracking_info._rating_sum

    @property
    def review_count(self) -> int:
        return self._tracking_info.review_count

    @property
    def view_count(self) -> int:
        return self._tracking_info.view_count

    @property
    def favorite_count(self) -> int:
        return self._tracking_info.favorite_count

    @property
    def version(self) -> int:
        return self._tracking_info.version

    @property
    def created_at(self) -> datetime:
        return self._timestamps.created_at

    @property
    def updated_at(self) -> datetime:
        return self._timestamps.updated_at

    @property
    def deleted_at(self) -> Optional[datetime]:
        return self._timestamps.deleted_at

    @property
    def is_deleted(self) -> bool:
        return self._timestamps.is_deleted()

    def __repr__(self) -> str:
        return f"Recipe(id={self.id}, name='{self.name}', author={self.author_id}, version={self.version})"

    def __str__(self) -> str:
        difficulty_str = self.difficulty.value if self.difficulty else "Unknown"
        return f"'{self.name}' by {self.author_id} ({difficulty_str})"

    def __eq__(self, other):
        if not isinstance(other, Recipe):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
