from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
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
    recipe_tags,
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

logger = logging.getLogger(__name__)


class RecipeMapper:
    """Handles mapping between Recipe domain entity and SQLAlchemy models"""

    @staticmethod
    def entity_to_dict(recipe: Recipe) -> Dict[str, Any]:
        """Convert Recipe entity to dictionary for persistence"""
        return {
            "name": recipe.name,
            "author_id": recipe.author_id.value if recipe.author_id else None,
            "description": recipe.description,
            "difficulty": recipe.difficulty.value if recipe.difficulty else None,
            "cuisine": recipe.cuisine.value if recipe.cuisine else None,
            "servings": (recipe.serving_info.servings if recipe.serving_info else None),
            "serving_size": (
                recipe.serving_info.serving_size if recipe.serving_info else None
            ),
            "prep_time_minutes": (
                recipe.cooking_time.prep_minutes if recipe.cooking_time else None
            ),
            "cook_time_minutes": (
                recipe.cooking_time.cook_minutes if recipe.cooking_time else None
            ),
            "calories": (
                recipe.nutritional_info.calories if recipe.nutritional_info else None
            ),
            "protein_g": (
                recipe.nutritional_info.protein_g if recipe.nutritional_info else None
            ),
            "carbs_g": (
                recipe.nutritional_info.carbs_g if recipe.nutritional_info else None
            ),
            "fat_g": (
                recipe.nutritional_info.fat_g if recipe.nutritional_info else None
            ),
            "rating_sum": recipe.rating_sum,
            "rating_count": recipe.rating_count,
            "view_count": recipe.view_count,
            "favorite_count": recipe.favorite_count,
            "version": recipe.version,
            "created_at": recipe.created_at,
            "updated_at": recipe.updated_at,
            "deleted_at": recipe.deleted_at,
        }

    @staticmethod
    async def model_to_entity(
        recipe_model: RecipeModel, session: AsyncSession
    ) -> Recipe:
        """Convert SQLAlchemy model to Recipe domain entity"""
        # Load related data with explicit logging
        logger.debug(f"Loading related data for recipe {recipe_model.id}")
        await session.refresh(
            recipe_model, ["ingredients", "steps", "tags", "meal_types"]
        )

        ingredients = RecipeMapper._map_ingredients(recipe_model.ingredients)
        logger.debug(
            f"Mapped {len(ingredients)} ingredients for recipe {recipe_model.id}"
        )

        steps = RecipeMapper._map_steps(recipe_model.steps)
        logger.debug(f"Mapped {len(steps)} steps for recipe {recipe_model.id}")

        tags = RecipeMapper._map_tags(recipe_model.tags)
        logger.debug(f"Mapped {len(tags)} tags for recipe {recipe_model.id}")

        meal_types = RecipeMapper._map_meal_types(recipe_model.meal_types)
        logger.debug(
            f"Mapped {len(meal_types)} meal types for recipe {recipe_model.id}"
        )

        serving_info = RecipeMapper._map_serving_info(recipe_model)
        cooking_time = RecipeMapper._map_cooking_time(recipe_model)
        nutritional_info = RecipeMapper._map_nutritional_info(recipe_model)

        difficulty = DifficultyLevel(recipe_model.difficulty)
        cuisine = CuisineType(recipe_model.cuisine) if recipe_model.cuisine else None

        logger.info(f"Successfully mapped recipe {recipe_model.id} to entity")

        return Recipe.reconstruct(
            id=RecipeId(recipe_model.id),
            name=recipe_model.name,
            author_id=UserId(recipe_model.author_id),
            description=recipe_model.description,
            difficulty=difficulty,
            cuisine=cuisine,
            ingredients=ingredients,
            steps=steps,
            tags=tags,
            meal_types=meal_types,
            serving_info=serving_info,
            cooking_time=cooking_time,
            nutritional_info=nutritional_info,
            rating_sum=recipe_model.rating_sum,
            rating_count=recipe_model.rating_count,
            view_count=recipe_model.view_count,
            favorite_count=recipe_model.favorite_count,
            version=recipe_model.version,
            created_at=recipe_model.created_at,
            updated_at=recipe_model.updated_at,
            deleted_at=recipe_model.deleted_at,
        )

    @staticmethod
    def _map_ingredients(ingredient_models: List[IngredientModel]) -> List[Ingredient]:
        """Map Ingredient models to domain entities"""
        ingredients = []
        for ing_model in ingredient_models:
            quantity = Quantity()
            if ing_model.quantity_value is not None:
                quantity = Quantity(
                    value=Decimal(str(ing_model.quantity_value)),
                    unit=ing_model.quantity_unit or "",
                )

            properties = IngredientProperties(
                is_vegan=ing_model.is_vegan,
                is_vegetarian=ing_model.is_vegetarian,
                is_gluten_free=ing_model.is_gluten_free,
                is_dairy_free=ing_model.is_dairy_free,
                allergens=set(ing_model.allergens) if ing_model.allergens else set(),
            )

            substitutes = RecipeMapper._parse_substitutes(ing_model.substitutes)

            ingredient = Ingredient.reconstruct(
                id=IngredientId(ing_model.id),
                name=ing_model.name,
                quantity=quantity,
                properties=properties,
                is_optional=ing_model.is_optional,
                substitutes=substitutes,
            )
            ingredients.append(ingredient)
        return ingredients

    @staticmethod
    def _map_steps(step_models: List[StepModel]) -> List[Step]:
        """Map Step models to domain entities"""
        return [
            Step(
                number=step.step_number,
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )
            for step in step_models
        ]

    @staticmethod
    def _map_tags(tag_models: List[TagModel]) -> set[Tag]:
        """Map Tag models to domain entities"""
        return {Tag(name=tag.name, description=tag.description) for tag in tag_models}

    @staticmethod
    def _map_meal_types(meal_type_models: List[RecipeMealTypeModel]) -> set[MealType]:
        """Map MealType models to domain entities"""
        return {MealType(meal_type.meal_type) for meal_type in meal_type_models}

    @staticmethod
    def _map_serving_info(recipe_model: RecipeModel) -> Optional[ServingInfo]:
        """Map serving info from model"""
        if recipe_model.serving_size and recipe_model.servings:
            return ServingInfo(
                servings=recipe_model.servings,
                serving_size=recipe_model.serving_size,
            )
        return None

    @staticmethod
    def _map_cooking_time(recipe_model: RecipeModel) -> Optional[CookingTime]:
        """Map cooking time from model"""
        if (
            recipe_model.prep_time_minutes is not None
            or recipe_model.cook_time_minutes is not None
        ):
            return CookingTime(
                prep_minutes=recipe_model.prep_time_minutes or 0,
                cook_minutes=recipe_model.cook_time_minutes or 0,
            )
        return None

    @staticmethod
    def _map_nutritional_info(recipe_model: RecipeModel) -> Optional[NutritionalInfo]:
        """Map nutritional info from model"""
        if recipe_model.calories is not None:
            return NutritionalInfo(
                calories=int(recipe_model.calories),
                protein_g=(
                    Decimal(str(recipe_model.protein_g))
                    if recipe_model.protein_g
                    else Decimal("0")
                ),
                carbs_g=(
                    Decimal(str(recipe_model.carbs_g))
                    if recipe_model.carbs_g
                    else Decimal("0")
                ),
                fat_g=(
                    Decimal(str(recipe_model.fat_g))
                    if recipe_model.fat_g
                    else Decimal("0")
                ),
            )
        return None

    @staticmethod
    def _parse_substitutes(substitutes_data) -> List[str]:
        """Parse substitutes from various formats"""
        if not substitutes_data:
            return []

        try:
            if isinstance(substitutes_data, str):
                return json.loads(substitutes_data)
            elif isinstance(substitutes_data, list):
                return substitutes_data
            else:
                return [substitutes_data]
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(
                f"Failed to parse substitutes: {substitutes_data}, error: {e}"
            )
            return []
