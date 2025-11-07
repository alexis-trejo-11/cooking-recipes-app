from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import func, select, update, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.core.pagination import Page, PaginationParams
from app.utils.core.specification import SQLSpecification as Specification
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    Ingredient,
    MealType,
    Step,
    Tag,
    RecipeId,
)
from app.modules.recipe.infrastructure.persistence.models import (
    RecipeModel,
    IngredientModel,
    StepModel,
    TagModel,
    RecipeMealTypeModel,
    recipe_tags,
)
from app.modules.recipe.application.exceptions import RecipeNotFoundException
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
            .options(
                selectinload(RecipeModel.ingredients),
                selectinload(RecipeModel.steps),
                selectinload(RecipeModel.tags),
                selectinload(RecipeModel.meal_types),
            )
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
            .where(
                and_(
                    RecipeModel.id == recipe_id.value,
                    RecipeModel.author_id == author_id.value,
                    RecipeModel.deleted_at.is_(None),
                )
            )
            .options(
                selectinload(RecipeModel.ingredients),
                selectinload(RecipeModel.steps),
                selectinload(RecipeModel.tags),
                selectinload(RecipeModel.meal_types),
            )
        )
        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            logger.info(f"Recipe not found: {recipe_id.value}")
            return None

        logger.debug(f"Recipe found: {recipe_id.value}")
        return await self.mapper.model_to_entity(recipe_model, self.session)

    async def search(
        self, spec: Specification, page_request: PaginationParams
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

            # Apply joins
            for join in joins:
                if join not in [
                    RecipeModel.ingredients,
                    RecipeModel.steps,
                    RecipeModel.tags,
                    RecipeModel.meal_types,
                ]:
                    query = query.join(join)

            query = query.where(spec.to_sql_condition())

            # Count query
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

            # Apply sorting
            sort_column = self._get_sort_column(page_request.sort_by or "created_at")
            if page_request.sort_dir == "desc":
                sort_column = sort_column.desc()
            else:
                sort_column = sort_column.asc()

            query = query.order_by(sort_column)

            # Apply pagination
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
            logger.error(f"Error searching recipes with spec: {e}", exc_info=True)
            return Page.empty()

    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        """Check if recipe with same name exists for author"""
        logger.debug(
            f"Checking if recipe exists - name: '{name}', author: {author_id.value}"
        )

        stmt = select(
            select(RecipeModel.id)
            .where(
                and_(
                    RecipeModel.name == name,
                    RecipeModel.author_id == author_id.value,
                    RecipeModel.deleted_at.is_(None),
                )
            )
            .exists()
        )
        result = await self.session.execute(stmt)
        exists = result.scalar() or False

        logger.debug(
            f"Recipe exists check - name: '{name}', author: {author_id.value}, result: {exists}"
        )
        return exists

    async def save(self, recipe: Recipe) -> Recipe:
        """Save recipe (create or update)"""
        if recipe.id and recipe.id.value > 0:
            logger.info(f"Updating existing recipe: {recipe.id.value}")
            return await self._update(recipe)
        else:
            logger.info("Creating new recipe")
            return await self._create(recipe)

    async def delete(self, recipe_id: RecipeId) -> bool:
        """Soft delete recipe by ID"""
        logger.info(f"Soft deleting recipe: {recipe_id.value}")

        stmt = (
            update(RecipeModel)
            .where(
                and_(
                    RecipeModel.id == recipe_id.value,
                    RecipeModel.deleted_at.is_(None),
                )
            )
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

    async def _create(self, recipe: Recipe) -> Recipe:
        """Create new recipe with all related entities in a single transaction"""
        try:
            # 1. Create main recipe
            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_model = RecipeModel(**recipe_data)
            self.session.add(recipe_model)
            await self.session.flush()  # Get the ID without committing

            recipe_id = recipe_model.id
            logger.debug(f"Created recipe with ID: {recipe_id}")

            # 2. Create all related entities (they'll use the recipe_id)
            await self._create_ingredients(recipe_id, recipe.ingredients)
            await self._create_steps(recipe_id, recipe.steps)
            await self._associate_tags(recipe_id, list(recipe.tags))
            await self._create_meal_types(recipe_id, list(recipe.meal_types))

            # 3. Single commit for all operations
            await self.session.commit()
            logger.info(f"Successfully created recipe: {recipe_id}")

            # 4. Return fresh instance with all relationships loaded
            created_recipe = await self.find_by_id(RecipeId(recipe_id))
            if created_recipe is None:
                raise RuntimeError(
                    f"Failed to retrieve newly created recipe with ID: {recipe_id}"
                )
            return created_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating recipe: {e}", exc_info=True)
            raise

    async def _update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe with all related entities in a single transaction"""
        try:
            if not recipe.id:
                raise RecipeNotFoundException("Recipe ID is required for update")

            recipe_id = recipe.id.value
            logger.debug(f"Starting update for recipe: {recipe_id}")

            # Update main recipe data
            updated_version = recipe.version + 1
            current_time = datetime.now(timezone.utc)

            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_data["version"] = updated_version
            recipe_data["updated_at"] = current_time

            stmt = (
                update(RecipeModel)
                .where(
                    and_(
                        RecipeModel.id == recipe_id,
                        RecipeModel.deleted_at.is_(None),
                    )
                )
                .values(**recipe_data)
            )

            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                logger.warning(f"Recipe not found for update: {recipe_id}")
                raise RecipeNotFoundException(f"Recipe with ID {recipe.id} not found")

            # Delete old related entities
            await self._delete_ingredients(recipe_id)
            await self._delete_steps(recipe_id)
            await self._delete_meal_types(recipe_id)
            await self._delete_tag_associations(recipe_id)

            # Create new related entities
            await self._create_ingredients(recipe_id, recipe.ingredients)
            await self._create_steps(recipe_id, recipe.steps)
            await self._associate_tags(recipe_id, list(recipe.tags))
            await self._create_meal_types(recipe_id, list(recipe.meal_types))

            await self.session.commit()
            logger.info(f"Successfully updated recipe: {recipe_id}")

            updated_recipe = await self.find_by_id(recipe.id)
            if updated_recipe is None:
                raise RuntimeError(
                    f"Failed to retrieve updated recipe with ID: {recipe_id}"
                )
            return updated_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating recipe {recipe.id}: {e}", exc_info=True)
            raise

    async def _create_ingredients(self, recipe_id: int, ingredients: List[Ingredient]):
        """Bulk create ingredients for a recipe"""
        if not ingredients:
            return

        ingredient_models = [
            IngredientModel(
                recipe_id=recipe_id,
                name=ing.name,
                quantity_value=ing.quantity.value if ing.quantity else 0,
                quantity_unit=ing.quantity.unit if ing.quantity else "",
                is_optional=ing.is_optional,
                is_vegan=ing.properties.is_vegan,
                is_vegetarian=ing.properties.is_vegetarian,
                is_gluten_free=ing.properties.is_gluten_free,
                is_dairy_free=ing.properties.is_dairy_free,
                allergens=list(ing.properties.allergens),
                substitutes=ing.substitutes,
            )
            for ing in ingredients
        ]
        self.session.add_all(ingredient_models)
        logger.debug(
            f"Created {len(ingredient_models)} ingredients for recipe {recipe_id}"
        )

    async def _create_steps(self, recipe_id: int, steps: List[Step]):
        """Bulk create steps for a recipe"""
        if not steps:
            return

        step_models = [
            StepModel(
                recipe_id=recipe_id,
                step_number=step.number,
                description=step.description,
                duration_minutes=step.duration_minutes,
                technique=step.technique,
                temperature=step.temperature,
            )
            for step in steps
        ]
        self.session.add_all(step_models)
        logger.debug(f"Created {len(step_models)} steps for recipe {recipe_id}")

    async def _associate_tags(self, recipe_id: int, tags: List[Tag]):
        """Associate tags with recipe (create tags if needed)"""
        if not tags:
            return

        for tag in tags:
            # Get or create tag
            tag_model = await self._get_or_create_tag(tag)

            # Check if association already exists
            check_stmt = select(recipe_tags).where(
                and_(
                    recipe_tags.c.recipe_id == recipe_id,
                    recipe_tags.c.tag_id == tag_model.id,
                )
            )
            result = await self.session.execute(check_stmt)

            if result.first() is None:
                # Create association
                stmt = recipe_tags.insert().values(
                    recipe_id=recipe_id, tag_id=tag_model.id
                )
                await self.session.execute(stmt)

        logger.debug(f"Associated {len(tags)} tags with recipe {recipe_id}")

    async def _get_or_create_tag(self, tag: Tag) -> TagModel:
        """Get existing tag or create new one"""
        stmt = select(TagModel).where(TagModel.name == tag.name)
        result = await self.session.execute(stmt)
        tag_model = result.scalar_one_or_none()

        if not tag_model:
            tag_model = TagModel(name=tag.name, description=tag.description)
            self.session.add(tag_model)
            await self.session.flush()  # Get the ID
            logger.debug(f"Created new tag: {tag.name}")

        return tag_model

    async def _create_meal_types(self, recipe_id: int, meal_types: List[MealType]):
        """Bulk create meal types for a recipe"""
        if not meal_types:
            return

        meal_type_models = [
            RecipeMealTypeModel(
                recipe_id=recipe_id,
                meal_type=meal_type.value,
            )
            for meal_type in meal_types
        ]
        self.session.add_all(meal_type_models)
        logger.debug(
            f"Created {len(meal_type_models)} meal types for recipe {recipe_id}"
        )

    async def _delete_ingredients(self, recipe_id: int):
        """Delete all ingredients for a recipe"""
        stmt = delete(IngredientModel).where(IngredientModel.recipe_id == recipe_id)
        result = await self.session.execute(stmt)
        logger.debug(f"Deleted {result.rowcount} ingredients for recipe {recipe_id}")

    async def _delete_steps(self, recipe_id: int):
        """Delete all steps for a recipe"""
        stmt = delete(StepModel).where(StepModel.recipe_id == recipe_id)
        result = await self.session.execute(stmt)
        logger.debug(f"Deleted {result.rowcount} steps for recipe {recipe_id}")

    async def _delete_meal_types(self, recipe_id: int):
        """Delete all meal types for a recipe"""
        stmt = delete(RecipeMealTypeModel).where(
            RecipeMealTypeModel.recipe_id == recipe_id
        )
        result = await self.session.execute(stmt)
        logger.debug(f"Deleted {result.rowcount} meal types for recipe {recipe_id}")

    async def _delete_tag_associations(self, recipe_id: int):
        """Delete all tag associations for a recipe"""
        stmt = delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        result = await self.session.execute(stmt)
        logger.debug(
            f"Deleted {result.rowcount} tag associations for recipe {recipe_id}"
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
