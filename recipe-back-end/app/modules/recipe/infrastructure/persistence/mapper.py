from typing import Optional, List, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    RecipeReconstructData,
    RecipeId,
    IngredientId,
    DifficultyLevel,
    CuisineType,
    MealType,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.ingredient import (
    Ingredient,
    IngredientProperties,
)
from app.modules.recipe.infrastructure.persistence.models import (
    RecipeModel,
    IngredientModel,
    StepModel,
    TagModel,
    RecipeMealTypeModel,
)
from app.modules.recipe.domain.models.value_objects.value_objects_standard import (
    Step,
    Tag,
    ServingInfo,
    CookingTime,
    NutritionalInfo,
    Quantity,
)
from decimal import Decimal
import json
import logging

logger = logging.getLogger("app.modules.recipe")


class RecipeMapper:
    """
    Mapper simplificado que se enfoca en transformar datos,
    no en cargar relaciones.
    """

    @staticmethod
    def model_to_entity(recipe_model: RecipeModel) -> Recipe:
        """
        Convierte SQLAlchemy model a Recipe entity.

        IMPORTANTE: Asume que recipe_model ya tiene las relaciones cargadas.

        Args:
            recipe_model: Modelo con relaciones cargadas (ingredients, steps, etc)

        Returns:
            Recipe: Entidad de dominio

        Raises:
            ValueError: Si faltan relaciones requeridas
        """
        try:
            # Validar que las relaciones estén cargadas
            if not hasattr(recipe_model, "ingredients"):
                raise ValueError("Recipe model must have ingredients loaded")

            # Preparar datos para reconstruct
            data = RecipeReconstructData(
                id=RecipeId(recipe_model.id),
                name=recipe_model.name,
                author_id=UserId(recipe_model.author_id),
                description=recipe_model.description or "",
                difficulty=DifficultyLevel(recipe_model.difficulty),
                cuisine=CuisineType(recipe_model.cuisine),
                # Mapear colecciones
                ingredients=RecipeMapper._map_ingredients(recipe_model.ingredients),
                steps=RecipeMapper._map_steps(recipe_model.steps),
                tags=RecipeMapper._map_tags(recipe_model.tags),
                meal_types=RecipeMapper._map_meal_types(recipe_model.meal_types),
                # Mapear metadata
                serving_info=RecipeMapper._map_serving_info(recipe_model),
                cooking_time=RecipeMapper._map_cooking_time(recipe_model),
                nutritional_info=RecipeMapper._map_nutritional_info(recipe_model),
                # Tracking info
                rating_sum=recipe_model.rating_sum or 0,
                rating_count=recipe_model.rating_count or 0,
                view_count=recipe_model.view_count or 0,
                favorite_count=recipe_model.favorite_count or 0,
                version=recipe_model.version or 1,
                # Timestamps
                created_at=recipe_model.created_at,
                updated_at=recipe_model.updated_at,
                deleted_at=recipe_model.deleted_at,
            )

            # Usar el reconstruct de Recipe
            return Recipe.reconstruct(data)

        except Exception as e:
            logger.error(
                f"Error mapping recipe model {recipe_model.id}: {e}", exc_info=True
            )
            raise

    @staticmethod
    def entity_to_dict(recipe: Recipe) -> dict:
        """
        Convierte Recipe entity a diccionario para persistencia.

        Args:
            recipe: Entidad de dominio

        Returns:
            dict: Datos para crear/actualizar modelo de SQLAlchemy
        """
        return {
            "name": recipe.name,
            "author_id": recipe.author_id.value,
            "description": recipe.description,
            "difficulty": recipe.difficulty.value,
            "cuisine": recipe.cuisine.value,
            # Serving info
            "servings": recipe.serving_info.servings if recipe.serving_info else None,
            "serving_size": (
                recipe.serving_info.serving_size if recipe.serving_info else None
            ),
            # Cooking time
            "prep_time_minutes": (
                recipe.cooking_time.prep_minutes if recipe.cooking_time else None
            ),
            "cook_time_minutes": (
                recipe.cooking_time.cook_minutes if recipe.cooking_time else None
            ),
            "rest_time_minutes": (
                recipe.cooking_time.rest_minutes if recipe.cooking_time else None
            ),
            # Nutritional info (opcional)
            "calories": (
                recipe.nutritional_info.calories if recipe.nutritional_info else None
            ),
            "protein_g": (
                float(recipe.nutritional_info.protein_g)
                if recipe.nutritional_info and recipe.nutritional_info.protein_g
                else None
            ),
            "carbs_g": (
                float(recipe.nutritional_info.carbs_g)
                if recipe.nutritional_info and recipe.nutritional_info.carbs_g
                else None
            ),
            "fat_g": (
                float(recipe.nutritional_info.fat_g)
                if recipe.nutritional_info and recipe.nutritional_info.fat_g
                else None
            ),
            # Tracking
            "rating_sum": recipe.rating_sum,
            "rating_count": recipe.rating_count,
            "view_count": recipe.view_count,
            "favorite_count": recipe.favorite_count,
            "version": recipe.version,
            # Timestamps
            "created_at": recipe.created_at,
            "updated_at": recipe.updated_at,
            "deleted_at": recipe.deleted_at,
        }

    @staticmethod
    def _map_ingredients(ingredient_models: List[IngredientModel]) -> List[Ingredient]:
        """Mapea ingredientes de modelo a entidad"""
        if not ingredient_models:
            return []

        ingredients = []
        for ing_model in ingredient_models:
            try:
                quantity = Quantity(
                    value=Decimal(str(ing_model.quantity_value or 0)),
                    unit=ing_model.quantity_unit or "units",
                )

                properties = IngredientProperties(
                    is_vegan=ing_model.is_vegan or False,
                    is_vegetarian=ing_model.is_vegetarian or False,
                    is_gluten_free=ing_model.is_gluten_free or False,
                    is_dairy_free=ing_model.is_dairy_free or False,
                    allergens=(
                        set(ing_model.allergens) if ing_model.allergens else set()
                    ),
                )

                substitutes = RecipeMapper._parse_json_field(ing_model.substitutes)

                ingredient = Ingredient.reconstruct(
                    id=IngredientId(ing_model.id),
                    name=ing_model.name,
                    quantity=quantity,
                    properties=properties,
                    is_optional=ing_model.is_optional or False,
                    substitutes=substitutes,
                )

                ingredients.append(ingredient)

            except Exception as e:
                logger.error(f"Error mapping ingredient {ing_model.id}: {e}")
                # Continuar con los demás ingredientes
                continue

        return ingredients

    @staticmethod
    def _map_steps(step_models: List[StepModel]) -> List[Step]:
        """Mapea pasos de modelo a value object"""
        if not step_models:
            return []

        # Ordenar por step_number
        sorted_steps = sorted(step_models, key=lambda x: x.step_number)

        return [
            Step(
                number=step.step_number,
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )
            for step in sorted_steps
        ]

    @staticmethod
    def _map_tags(tag_models: List[TagModel]) -> Set[Tag]:
        """Mapea tags de modelo a value object"""
        if not tag_models:
            return set()

        return {Tag(name=tag.name, description=tag.description) for tag in tag_models}

    @staticmethod
    def _map_meal_types(meal_type_models: List[RecipeMealTypeModel]) -> Set[MealType]:
        """Mapea meal types de modelo a enum"""
        meal_types = set()

        if not meal_type_models:
            return meal_types

        for mt_model in meal_type_models:
            try:
                meal_types.add(MealType(mt_model.meal_type))
            except ValueError as e:
                logger.warning(f"Invalid meal type '{mt_model.meal_type}': {e}")
                continue

        return meal_types

    @staticmethod
    def _map_serving_info(recipe_model: RecipeModel) -> ServingInfo:
        """Mapea serving info de modelo a value object"""
        return ServingInfo(
            servings=recipe_model.servings,
            serving_size=recipe_model.serving_size,
        )

    @staticmethod
    def _map_cooking_time(recipe_model: RecipeModel) -> CookingTime:
        """Mapea cooking time de modelo a value object"""
        prep = recipe_model.prep_time_minutes or 0
        cook = recipe_model.cook_time_minutes or 0
        rest = recipe_model.rest_time_minutes or 0

        return CookingTime(
            prep_minutes=prep,
            cook_minutes=cook,
            rest_minutes=rest,
        )

    @staticmethod
    def _map_nutritional_info(recipe_model: RecipeModel) -> Optional[NutritionalInfo]:
        """Mapea nutritional info de modelo a value object"""
        if recipe_model.calories is None:
            return None

        return NutritionalInfo(
            calories=int(recipe_model.calories),
            protein_g=(
                Decimal(str(recipe_model.protein_g)) if recipe_model.protein_g else None
            ),
            carbs_g=(
                Decimal(str(recipe_model.carbs_g)) if recipe_model.carbs_g else None
            ),
            fat_g=Decimal(str(recipe_model.fat_g)) if recipe_model.fat_g else None,
        )

    @staticmethod
    def _parse_json_field(field_data) -> List[str]:
        """
        Parse campos JSON que pueden venir en diferentes formatos.

        Args:
            field_data: Datos a parsear (string JSON, lista, etc)

        Returns:
            Lista de strings
        """
        if not field_data:
            return []

        try:
            if isinstance(field_data, str):
                # Si es string JSON, parsearlo
                if field_data.startswith("["):
                    return json.loads(field_data)
                # Si es string simple, retornar como lista
                return [field_data]
            elif isinstance(field_data, list):
                return field_data
            else:
                return [str(field_data)]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON field: {field_data}")
            return []
