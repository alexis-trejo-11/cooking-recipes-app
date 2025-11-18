import logging
import json
from decimal import Decimal
from typing import Optional, List
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
from app.utils.core.exceptions.modules import MappingException

logger = logging.getLogger(__name__)


class RecipeMapper:
    """
    Translates between domain entities and persistence models.

    This mapper assumes that all relationships are eagerly loaded
    before calling model_to_entity().
    """

    @staticmethod
    def model_to_entity(
        recipe_model: RecipeModel,
        rating_sum: Optional[int] = None,
        rating_count: Optional[int] = None,
        favorite_count: Optional[int] = None,
    ) -> Recipe:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            recipe_model: Model with eagerly loaded relationships
            rating_sum: Override rating sum (optional)
            rating_count: Override rating count (optional)
            view_count: Override view count (optional)
            favorite_count: Override favorite count (optional)

        Returns:
            Recipe domain entity

        Raises:
            MappingException: If required relationships are not loaded
        """
        if not hasattr(recipe_model, "ingredients"):
            raise MappingException(
                "Recipe model must have ingredients relationship loaded"
            )

        data = RecipeReconstructData(
            id=RecipeId(recipe_model.id),
            name=recipe_model.name,
            author_id=UserId(recipe_model.author_id),
            description=recipe_model.description or "",
            difficulty=DifficultyLevel(recipe_model.difficulty),
            cuisine=CuisineType(recipe_model.cuisine),
            ingredients=RecipeMapper._map_ingredients(recipe_model.ingredients),
            steps=RecipeMapper._map_steps(recipe_model.steps),
            tags=RecipeMapper._map_tags(recipe_model.tags),
            meal_types=RecipeMapper._map_meal_types(recipe_model.meal_types),
            serving_info=RecipeMapper._map_serving_info(recipe_model),
            cooking_time=RecipeMapper._map_cooking_time(recipe_model),
            nutritional_info=RecipeMapper._map_nutritional_info(recipe_model),
            rating_sum=rating_sum or 0,
            review_count=rating_count or 0,
            view_count=recipe_model.view_count or 0,
            favorite_count=favorite_count or 0,
            version=recipe_model.version or 1,
            created_at=recipe_model.created_at,
            updated_at=recipe_model.updated_at,
            deleted_at=recipe_model.deleted_at,
        )

        return Recipe.reconstruct(data)

    @staticmethod
    def entity_to_dict(recipe: Recipe) -> dict:
        """
        Convert domain entity to dictionary for persistence.

        Args:
            recipe: Domain entity

        Returns:
            Dictionary with model fields
        """
        return {
            "name": recipe.name,
            "author_id": recipe.author_id.value,
            "description": recipe.description,
            "difficulty": recipe.difficulty.value,
            "cuisine": recipe.cuisine.value,
            "servings": recipe.serving_info.servings if recipe.serving_info else None,
            "serving_size": (
                recipe.serving_info.serving_size if recipe.serving_info else None
            ),
            "prep_time_minutes": (
                recipe.cooking_time.prep_minutes if recipe.cooking_time else None
            ),
            "cook_time_minutes": (
                recipe.cooking_time.cook_minutes if recipe.cooking_time else None
            ),
            "rest_time_minutes": (
                recipe.cooking_time.rest_minutes if recipe.cooking_time else None
            ),
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
            "rating_sum": recipe.rating_sum,
            "review_count": recipe.review_count,
            "view_count": recipe.view_count,
            "favorite_count": recipe.favorite_count,
            "version": recipe.version,
            "created_at": recipe.created_at,
            "updated_at": recipe.updated_at,
            "deleted_at": recipe.deleted_at,
        }

    @staticmethod
    def _map_ingredients(ingredient_models: List[IngredientModel]) -> List[Ingredient]:
        """Map ingredient models to domain entities."""
        if not ingredient_models:
            return []

        ingredients = []
        for model in ingredient_models:
            try:
                quantity = Quantity(
                    value=Decimal(str(model.quantity_value or 0)),
                    unit=model.quantity_unit or "units",
                )

                properties = IngredientProperties(
                    is_vegan=model.is_vegan or False,
                    is_vegetarian=model.is_vegetarian or False,
                    is_gluten_free=model.is_gluten_free or False,
                    is_dairy_free=model.is_dairy_free or False,
                    allergens=set(model.allergens) if model.allergens else set(),
                )

                substitutes = RecipeMapper._parse_json_list(model.substitutes)

                ingredient = Ingredient.reconstruct(
                    id=IngredientId(model.id),
                    name=model.name,
                    quantity=quantity,
                    properties=properties,
                    is_optional=model.is_optional or False,
                    substitutes=substitutes,
                )

                ingredients.append(ingredient)

            except Exception as e:
                logger.error(f"Error mapping ingredient {model.id}: {e}")
                continue

        return ingredients

    @staticmethod
    def _map_steps(step_models: List[StepModel]) -> List[Step]:
        """Map step models to value objects."""
        if not step_models:
            return []

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
    def _map_tags(tag_models: List[TagModel]) -> set[Tag]:
        """Map tag models to value objects."""
        if not tag_models:
            return set()

        return {Tag(name=tag.name, description=tag.description) for tag in tag_models}

    @staticmethod
    def _map_meal_types(meal_type_models: List[RecipeMealTypeModel]) -> set[MealType]:
        """Map meal type models to enums."""
        meal_types = set()

        if not meal_type_models:
            return meal_types

        for model in meal_type_models:
            try:
                meal_types.add(MealType(model.meal_type))
            except MappingException as e:
                logger.warning(f"Invalid meal type '{model.meal_type}': {e}")
                continue

        return meal_types

    @staticmethod
    def _map_serving_info(recipe_model: RecipeModel) -> ServingInfo:
        """Map serving info from model to value object."""
        return ServingInfo(
            servings=recipe_model.servings,
            serving_size=recipe_model.serving_size,
        )

    @staticmethod
    def _map_cooking_time(recipe_model: RecipeModel) -> CookingTime:
        """Map cooking time from model to value object."""
        return CookingTime(
            prep_minutes=recipe_model.prep_time_minutes or 0,
            cook_minutes=recipe_model.cook_time_minutes or 0,
            rest_minutes=recipe_model.rest_time_minutes or 0,
        )

    @staticmethod
    def _map_nutritional_info(recipe_model: RecipeModel) -> Optional[NutritionalInfo]:
        """Map nutritional info from model to value object."""
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
    def _parse_json_list(field_data) -> List[str]:
        """Parse JSON fields that may come in different formats."""
        if not field_data:
            return []

        try:
            if isinstance(field_data, str):
                if field_data.startswith("["):
                    return json.loads(field_data)
                return [field_data]
            elif isinstance(field_data, list):
                return field_data
            else:
                return [str(field_data)]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON field: {field_data}")
            return []
