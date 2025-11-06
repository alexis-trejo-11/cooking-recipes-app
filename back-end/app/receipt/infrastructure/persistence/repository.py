from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from ....utils.core.pagination import Page, PageRequest
from ....utils.core.specification import SQLCriteria, SQLSpecification as Specification
from app.receipt.domain.interfaces import RecipeRepository
from app.receipt.domain.models.entities.recipe import (
    Recipe,
    Ingredient,
    MealType,
    Step,
    Tag,
    RecipeId,
)
from app.auth.domain.user import UserId
from app.receipt.infrastructure.persistence.models import (
    RecipeModel,
    IngredientModel,
    StepModel,
    TagModel,
    recipe_tags,
)
from app.receipt.application.exceptions import RecipeNotFoundException
import logging
from .mapper import RecipeMapper

logger = logging.getLogger(__name__)


class SQLAlchemyRecipeRepository(RecipeRepository):
    """SQLAlchemy implementation of RecipeRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = RecipeMapper()

    async def find_by_id(self, recipe_id: RecipeId) -> Optional[Recipe]:
        """Get recipe by ID with all related data"""
        logger.debug(f"Fetching recipe by ID: {recipe_id.value}")

        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == recipe_id.value)
            .where(RecipeModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            logger.info(f"Recipe not found: {recipe_id.value}")
            return None

        logger.debug(f"Recipe found: {recipe_id.value}")
        return await self.mapper.model_to_entity(recipe_model, self.session)

    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        logger.debug(
            f"Fetching recipe by ID: {recipe_id.value} and author ID: {author_id.value}"
        )

        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == recipe_id.value)
            .where(RecipeModel.author_id == author_id.value)
            .where(RecipeModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            logger.info(f"Recipe not found: {recipe_id.value}")
            return None

        logger.debug(f"Recipe found: {recipe_id.value}")
        return await self.mapper.model_to_entity(recipe_model, self.session)

    async def search(
        self, spec: Specification, page_request: PageRequest
    ) -> Page[Recipe]:
        """
        Search recipes using specification with pagination.

        Args:
            spec: Specification to filter recipes
            page_request: Pagination details

        Returns:
            Page[Recipe]: Paginated results
        """
        try:
            query = select(RecipeModel)

            joins = spec.get_joins()
            for join in joins:
                if join not in [
                    RecipeModel.ingredients,
                    RecipeModel.steps,
                    RecipeModel.tags,
                    RecipeModel.meal_types,
                ]:
                    query = query.join(join)

            query = query.where(spec.to_sql_condition())

            count_query = select(func.count()).select_from(RecipeModel)
            for join in joins:
                if join not in [
                    RecipeModel.ingredients,
                    RecipeModel.steps,
                    RecipeModel.tags,
                    RecipeModel.meal_types,
                ]:
                    count_query = count_query.join(join)
            count_query = count_query.where(spec.to_sql_condition())

            total_result = await self.session.execute(count_query)
            total = total_result.scalar() or 0

            sort_column = self._get_sort_column(page_request.sort_by or "created_at")
            if page_request.sort_dir == "desc":
                sort_column = sort_column.desc()
            else:
                sort_column = sort_column.asc()

            query = query.order_by(sort_column)

            offset = (page_request.page - 1) * page_request.size
            query = query.offset(offset).limit(page_request.size)

            # Eager load related data
            query = query.options(
                selectinload(RecipeModel.ingredients),
                selectinload(RecipeModel.steps),
                selectinload(RecipeModel.tags),
                selectinload(RecipeModel.meal_types),
            )

            result = await self.session.execute(query)
            recipe_models = result.scalars().all()

            recipes = [
                await self.mapper.model_to_entity(model, self.session)
                for model in recipe_models
            ]

            return Page(
                items=recipes,
                total=total,
                page=page_request.page,
                size=page_request.size,
            )
        except Exception as e:
            print(f"Error searching recipes with spec: {e}")
            return Page.empty()

    async def count_by_spec(self, spec: SQLCriteria) -> int:
        """Count recipes that satisfy the specification."""
        try:
            query = select(func.count()).select_from(RecipeModel)

            # Apply joins from specification
            joins = spec.get_joins()
            for join in joins:
                if join not in [
                    RecipeModel.ingredients,
                    RecipeModel.steps,
                    RecipeModel.tags,
                    RecipeModel.meal_types,
                ]:
                    query = query.join(join)

            # Apply WHERE condition
            query = query.where(spec.to_sql_condition())

            result = await self.session.execute(query)
            return result.scalar() or 0

        except Exception as e:
            print(f"Error counting recipes with spec: {e}")
            return 0

    async def save(self, recipe: Recipe) -> Recipe:
        """Save recipe (create or update)"""
        if recipe.id and recipe.id.value > 0:
            logger.info(f"Updating existing recipe: {recipe.id.value}")
            return await self._update(recipe)
        else:
            logger.info("Creating new recipe")
            return await self._create(recipe)

    async def _create(self, recipe: Recipe) -> Recipe:
        """Create new recipe"""
        try:
            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_model = RecipeModel(**recipe_data)

            self.session.add(recipe_model)
            await self.session.flush()

            # Save related entities
            await self._save_related_entities(recipe_model.id, recipe)
            await self.session.commit()

            logger.info(f"Successfully created recipe: {recipe_model.id}")

            created_recipe = await self.find_by_id(RecipeId(recipe_model.id))
            if created_recipe is None:
                raise RuntimeError(
                    f"Failed to retrieve newly created recipe with ID: {recipe_model.id}"
                )
            return created_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating recipe: {e}", exc_info=True)
            raise

    async def _update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe"""
        try:
            if not recipe.id:
                raise RecipeNotFoundException("Recipe ID is required for update")

            logger.debug(f"Starting update for recipe: {recipe.id.value}")

            updated_version = recipe.version + 1
            current_time = datetime.now(timezone.utc)

            # Update main recipe data
            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_data["version"] = updated_version
            recipe_data["updated_at"] = current_time
            stmt = (
                update(RecipeModel)
                .where(RecipeModel.id == recipe.id.value)
                .where(RecipeModel.deleted_at.is_(None))
                .values(**recipe_data)
            )

            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                logger.warning(f"Recipe not found for update: {recipe.id.value}")
                raise RecipeNotFoundException(f"Recipe with ID {recipe.id} not found")

            # Update related entities
            await self._delete_related_entities(recipe.id.value)
            await self._save_related_entities(recipe.id.value, recipe)
            await self.session.commit()

            logger.info(f"Successfully updated recipe: {recipe.id.value}")
            return recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating recipe {recipe.id}: {e}", exc_info=True)
            raise

    async def _save_related_entities(self, recipe_id: int, recipe: Recipe):
        """Save all related entities for a recipe"""
        logger.debug(f"Saving related entities for recipe: {recipe_id}")

        await self._save_ingredients(recipe_id, recipe.get_ingredients())
        await self._save_steps(recipe_id, recipe.get_steps())
        await self._save_tags(recipe_id, list(recipe.get_tags()))
        await self._save_meal_types(recipe_id, list(recipe.get_meal_types()))

        logger.debug(f"Completed saving related entities for recipe: {recipe_id}")

    async def delete(self, recipe_id: RecipeId) -> bool:
        """Soft delete recipe by ID"""
        logger.info(f"Soft deleting recipe: {recipe_id.value}")

        stmt = (
            update(RecipeModel)
            .where(RecipeModel.id == recipe_id.value)
            .where(RecipeModel.deleted_at.is_(None))
            .values(deleted_at=func.now())
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Successfully soft deleted recipe: {recipe_id.value}")
        else:
            logger.warning(f"Recipe not found for deletion: {recipe_id.value}")

        return deleted

    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        """Check if recipe with same name exists for author"""
        logger.debug(
            f"Checking if recipe exists - name: '{name}', author: {author_id.value}"
        )

        stmt = (
            select(RecipeModel.id)
            .where(RecipeModel.name == name)
            .where(RecipeModel.author_id == author_id.value)
            .where(RecipeModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        exists = result.scalar_one_or_none() is not None

        logger.debug(
            f"Recipe exists check - name: '{name}', author: {author_id.value}, result: {exists}"
        )
        return exists

    # Helper methods for saving related entities (keep these as they are specific to persistence)
    async def _save_ingredients(self, recipe_id: int, ingredients: List[Ingredient]):
        """Save ingredients for a recipe"""
        for ingredient in ingredients:
            ingredient_model = IngredientModel(
                recipe_id=recipe_id,
                name=ingredient.name,
                quantity_value=(
                    ingredient.quantity.value if ingredient.quantity else None
                ),
                quantity_unit=ingredient.quantity.unit if ingredient.quantity else None,
                is_optional=ingredient.is_optional,
                is_vegan=ingredient.properties.is_vegan,
                is_vegetarian=ingredient.properties.is_vegetarian,
                is_gluten_free=ingredient.properties.is_gluten_free,
                is_dairy_free=ingredient.properties.is_dairy_free,
                allergens=list(ingredient.properties.allergens),
                substitutes=ingredient.substitutes,
            )
            self.session.add(ingredient_model)

    async def _save_steps(self, recipe_id: int, steps: List[Step]):
        """Save steps for a recipe"""
        for step in steps:
            step_model = StepModel(
                recipe_id=recipe_id,
                step_number=step.number,
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )
            self.session.add(step_model)

    async def _save_tags(self, recipe_id: int, tags: List[Tag]):
        """Save tags for a recipe (get or create tags)"""
        for tag in tags:
            # Check if tag exists
            stmt = select(TagModel).where(TagModel.name == tag.name)
            result = await self.session.execute(stmt)
            tag_model = result.scalar_one_or_none()

            if not tag_model:
                tag_model = TagModel(name=tag.name, description=tag.description)
                self.session.add(tag_model)
                await self.session.flush()

            # Verificar si la asociación ya existe
            stmt = select(RecipeModel).where(RecipeModel.id == recipe_id)
            recipe_result = await self.session.execute(stmt)
            recipe_model = recipe_result.scalar_one()

            # Verificar si el tag ya está asociado usando una consulta directa
            check_stmt = select(recipe_tags).where(
                recipe_tags.c.recipe_id == recipe_id,
                recipe_tags.c.tag_id == tag_model.id,
            )
            check_result = await self.session.execute(check_stmt)
            association_exists = check_result.scalar_one_or_none() is not None

            if not association_exists:
                # Agregar la asociación directamente
                stmt = recipe_tags.insert().values(
                    recipe_id=recipe_id, tag_id=tag_model.id
                )
                await self.session.execute(stmt)

    async def _save_meal_types(self, recipe_id: int, meal_types: List[MealType]):
        """Save meal types for a recipe"""
        for meal_type in meal_types:
            meal_type_model = RecipeMealType(
                recipe_id=recipe_id,
                meal_type=meal_type.value,
            )
            self.session.add(meal_type_model)

    async def _delete_related_entities(self, recipe_id: int):
        """Delete all related entities for a recipe"""
        logger.debug(f"Deleting related entities for recipe: {recipe_id}")

        await self.session.execute(
            delete(IngredientModel).where(IngredientModel.recipe_id == recipe_id)
        )
        await self.session.execute(
            delete(StepModel).where(StepModel.recipe_id == recipe_id)
        )
        await self.session.execute(
            delete(RecipeMealType).where(RecipeMealType.recipe_id == recipe_id)
        )

        await self.session.execute(
            delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        )

    def _get_sort_column(self, sort_by: str):
        """Get SQLAlchemy column for sorting."""
        sort_columns = {
            "created_at": RecipeModel.created_at,
            "updated_at": RecipeModel.updated_at,
            "name": RecipeModel.name,
            "rating": (RecipeModel.rating_sum / RecipeModel.rating_count),
            "views": RecipeModel.view_count,
            "favorites": RecipeModel.favorite_count,
        }
        return sort_columns.get(sort_by, RecipeModel.created_at)
