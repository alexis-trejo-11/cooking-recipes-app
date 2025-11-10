from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import func, select, update, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.core.pagination import Page, PaginationParams
from app.utils.core.specification import Specification
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

logger = logging.getLogger("app.modules.recipe")


class SQLAlchemyRecipeRepository(RecipeRepository):
    """SQLAlchemy implementation of RecipeRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = RecipeMapper()

    async def find_by_id(
        self, recipe_id: RecipeId, include_deleted: bool = False
    ) -> Optional[Recipe]:
        """
        Get recipe by ID with all related data

        Args:
            recipe_id: ID of the recipe to find
            include_deleted: If True, includes soft-deleted recipes
        """
        logger.debug(f"Fetching recipe by ID: {recipe_id}")

        stmt = select(RecipeModel).where(RecipeModel.id == recipe_id.value)

        # Filter out deleted recipes unless explicitly requested
        if not include_deleted:
            stmt = stmt.where(RecipeModel.deleted_at.is_(None))

        stmt = stmt.options(
            selectinload(RecipeModel.ingredients),
            selectinload(RecipeModel.steps),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.meal_types),
        )

        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            logger.info(f"Recipe not found: {recipe_id}")
            return None

        logger.debug(f"Recipe found: {recipe_id}")
        return self.mapper.model_to_entity(recipe_model)

    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        logger.debug(
            f"Fetching recipe by ID: {recipe_id} and author ID: {author_id.value}"
        )

        stmt = (
            select(RecipeModel)
            .where(
                and_(
                    RecipeModel.id == recipe_id.value,
                    RecipeModel.author_id == author_id.value,
                    RecipeModel.deleted_at.is_(
                        None
                    ),  # Aquí sí filtrar por no eliminados
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
            logger.info(f"Recipe not found: {recipe_id}")
            return None

        logger.debug(f"Recipe found: {recipe_id}")
        return self.mapper.model_to_entity(recipe_model)

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

            recipes = [self.mapper.model_to_entity(model) for model in recipe_models]

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
        logger.info(f"Soft deleting recipe: {recipe_id}")

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
            logger.info(f"Successfully soft deleted recipe: {recipe_id}")
        else:
            logger.warning(f"Recipe not found for deletion: {recipe_id}")

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
            logger.debug(f"Creating ingredients: {len(recipe.ingredients)}")
            await self._create_ingredients(recipe_id, recipe.ingredients)

            logger.debug(f"Creating steps: {len(recipe.steps)}")
            await self._create_steps(recipe_id, recipe.steps)

            logger.debug(f"Creating tags: {len(recipe.tags)}")
            await self._associate_tags(recipe_id, list(recipe.tags))

            logger.debug(
                f"Creating meal_types: {len(recipe.meal_types)} - {[mt.value for mt in recipe.meal_types]}"
            )
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
                raise RecipeNotFoundException(recipe.id)

            recipe_id = recipe.id.value
            logger.debug(f"Starting update for recipe: {recipe_id}")

            # Update main recipe data
            current_time = datetime.now(timezone.utc)

            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_data["updated_at"] = current_time

            stmt = (
                update(RecipeModel)
                .where(RecipeModel.id == recipe_id)  # REMOVED deleted_at filter
                .values(**recipe_data)
            )

            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                logger.warning(f"Recipe not found for update: {recipe_id}")
                raise RecipeNotFoundException(recipe.id)

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

            # Expire all para forzar recarga desde DB
            self.session.expire_all()

            # Incluir deleted recipes en caso de que se esté actualizando una eliminada
            updated_recipe = await self.find_by_id(recipe.id, include_deleted=True)
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

        ingredient_models = []
        for ing in ingredients:
            # SIEMPRE crear nuevos ingredientes sin ID
            ingredient_model = IngredientModel(
                recipe_id=recipe_id,
                name=ing.name,
                quantity_value=float(ing.quantity.value) if ing.quantity else 0.0,
                quantity_unit=ing.quantity.unit if ing.quantity else "units",
                is_optional=ing.is_optional,
                is_vegan=ing.properties.is_vegan,
                is_vegetarian=ing.properties.is_vegetarian,
                is_gluten_free=ing.properties.is_gluten_free,
                is_dairy_free=ing.properties.is_dairy_free,
                allergens=(
                    list(ing.properties.allergens) if ing.properties.allergens else []
                ),
                substitutes=ing.substitutes or [],
            )
            ingredient_models.append(ingredient_model)

        if ingredient_models:
            self.session.add_all(ingredient_models)
            await self.session.flush()
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
        await self.session.flush()
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

        await self.session.flush()
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
            logger.debug(f"No meal types to create for recipe {recipe_id}")
            return

        meal_type_models = []
        for meal_type in meal_types:
            # Verificar que es un MealType enum
            if isinstance(meal_type, MealType):
                meal_type_value = meal_type.value
            elif isinstance(meal_type, str):
                meal_type_value = meal_type
            else:
                logger.warning(f"Invalid meal type type: {type(meal_type)}")
                continue

            meal_type_models.append(
                RecipeMealTypeModel(
                    recipe_id=recipe_id,
                    meal_type=meal_type_value,
                )
            )

        if meal_type_models:
            self.session.add_all(meal_type_models)
            await self.session.flush()
            logger.debug(
                f"Created {len(meal_type_models)} meal types for recipe {recipe_id}: {[mt.meal_type for mt in meal_type_models]}"
            )
        else:
            logger.warning(f"No valid meal types to create for recipe {recipe_id}")

    async def _delete_ingredients(self, recipe_id: int):
        """Delete all ingredients for a recipe"""
        stmt = delete(IngredientModel).where(IngredientModel.recipe_id == recipe_id)
        await self.session.execute(stmt)
        logger.debug(f"Deleted ingredients for recipe {recipe_id}")

    async def _delete_steps(self, recipe_id: int):
        """Delete all steps for a recipe"""
        stmt = delete(StepModel).where(StepModel.recipe_id == recipe_id)
        await self.session.execute(stmt)
        logger.debug(f"Deleted steps for recipe {recipe_id}")

    async def _delete_meal_types(self, recipe_id: int):
        """Delete all meal types for a recipe"""
        stmt = delete(RecipeMealTypeModel).where(
            RecipeMealTypeModel.recipe_id == recipe_id
        )
        await self.session.execute(stmt)
        logger.debug(f"Deleted meal types for recipe {recipe_id}")

    async def _delete_tag_associations(self, recipe_id: int):
        """Delete all tag associations for a recipe"""
        stmt = delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        await self.session.execute(stmt)
        logger.debug(f"Deleted tag associations for recipe {recipe_id}")

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
