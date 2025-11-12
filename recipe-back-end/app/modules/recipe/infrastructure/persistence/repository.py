from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import func, select, update, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.core.pagination import Page, PaginationParams
from app.utils.core.specification import Specification
from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeReviewRepository,
    RecipeFavoriteRepository,
)
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import (
    Recipe,
    Ingredient,
    MealType,
    Step,
    Tag,
    RecipeId,
)
from app.modules.recipe.domain.models.entities.review import Review
from app.modules.recipe.infrastructure.persistence.models import (
    RecipeModel,
    IngredientModel,
    StepModel,
    TagModel,
    RecipeMealTypeModel,
    recipe_tags,
    recipe_favorites,
    recipe_reviews,
)
from app.modules.recipe.application.exceptions import RecipeNotFoundException
import logging
from .mapper import RecipeMapper

logger = logging.getLogger("app.modules.recipe")


class SqlAlchemyRecipeRepository(RecipeRepository):
    """SQLAlchemy implementation of recipe aggregate repository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = RecipeMapper()
        self._meal_type_repo = _MealTypeRepository(session)
        self._ingredient_repo = _IngredientRepository(session)
        self._step_repo = _StepRepository(session)
        self._tag_repo = _TagRepository(session)

    async def find_by_id(
        self,
        recipe_id: RecipeId,
        include_deleted: bool = False,
        with_relations: bool = False,
    ) -> Optional[Recipe]:
        """
        Find recipe by ID.

        Args:
            recipe_id: Recipe identifier
            include_deleted: Include soft-deleted recipes
            with_relations: Eagerly load relationships

        Returns:
            Recipe entity or None if not found
        """
        stmt = select(RecipeModel).where(RecipeModel.id == recipe_id.value)

        if not include_deleted:
            stmt = stmt.where(RecipeModel.deleted_at.is_(None))

        if with_relations:
            stmt = self._apply_relationship_loading(stmt)

        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            return None

        return self.mapper.model_to_entity(recipe_model)

    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        """Find recipe by ID and author (for authorization checks)."""
        stmt = select(RecipeModel).where(
            and_(
                RecipeModel.id == recipe_id.value,
                RecipeModel.author_id == author_id.value,
                RecipeModel.deleted_at.is_(None),
            )
        )
        stmt = self._apply_relationship_loading(stmt)

        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            return None

        return self.mapper.model_to_entity(recipe_model)

    async def search(
        self, spec: Specification, page_request: PaginationParams
    ) -> Page[Recipe]:
        """
        Search recipes using specification pattern.

        Args:
            spec: Search specification
            page_request: Pagination parameters

        Returns:
            Paginated recipe results
        """
        try:
            query = select(RecipeModel)
            joins = spec.get_joins()

            for join in joins:
                if self._should_apply_join(join):
                    query = query.join(join)

            query = query.where(spec.to_sql_condition())

            total = await self._count_results(spec, joins)

            query = self._apply_sorting(query, page_request)
            query = self._apply_pagination(query, page_request)
            query = self._apply_relationship_loading(query)

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
            logger.error(f"Error searching recipes: {e}", exc_info=True)
            return Page.empty()

    async def exists_by_name_and_author(self, name: str, author_id: UserId) -> bool:
        """Check if recipe with same name exists for author."""
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
        return result.scalar() or False

    async def exists_by_id(
        self, recipe_id: RecipeId, include_deleted: bool = False
    ) -> bool:
        """Check if recipe exists by ID."""
        conditions = [RecipeModel.id == recipe_id.value]
        if not include_deleted:
            conditions.append(RecipeModel.deleted_at.is_(None))

        stmt = select(select(RecipeModel.id).where(and_(*conditions)).exists())
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def save(self, recipe: Recipe) -> Recipe:
        """
        Save recipe (create or update).

        Args:
            recipe: Recipe entity to save

        Returns:
            Saved recipe entity
        """
        if recipe.id and recipe.id.value > 0:
            return await self._update(recipe)
        else:
            return await self._create(recipe)

    async def delete(self, recipe_id: RecipeId) -> bool:
        """
        Soft delete recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            True if deleted, False if not found
        """
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

        return result.rowcount > 0

    async def increase_view_count(self, recipe_id: RecipeId) -> None:
        """Increment recipe view count."""
        stmt = (
            update(RecipeModel)
            .where(
                and_(
                    RecipeModel.id == recipe_id.value,
                    RecipeModel.deleted_at.is_(None),
                )
            )
            .values(view_count=RecipeModel.view_count + 1)
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def _create(self, recipe: Recipe) -> Recipe:
        """Create new recipe with all relationships."""
        try:
            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_model = RecipeModel(**recipe_data)
            self.session.add(recipe_model)
            await self.session.flush()

            recipe_id = recipe_model.id

            await self._ingredient_repo.create_all(recipe_id, recipe.ingredients)
            await self._step_repo.create_all(recipe_id, recipe.steps)
            await self._tag_repo.associate_tags(recipe_id, list(recipe.tags))
            await self._meal_type_repo.create_all(recipe_id, list(recipe.meal_types))

            await self.session.commit()

            created_recipe = await self.find_by_id(RecipeId(recipe_id))
            if created_recipe is None:
                raise RuntimeError(f"Failed to retrieve created recipe: {recipe_id}")

            return created_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating recipe: {e}", exc_info=True)
            raise

    async def _update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe with all relationships."""
        try:
            if not recipe.id:
                raise RecipeNotFoundException(recipe.id)

            recipe_id = recipe.id.value

            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_data["updated_at"] = datetime.now(timezone.utc)

            stmt = (
                update(RecipeModel)
                .where(RecipeModel.id == recipe_id)
                .values(**recipe_data)
            )

            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise RecipeNotFoundException(recipe.id)

            await self._delete_old_relationships(recipe_id)
            await self._create_new_relationships(recipe_id, recipe)

            await self.session.commit()
            self.session.expire_all()

            updated_recipe = await self.find_by_id(recipe.id, include_deleted=True)
            if updated_recipe is None:
                raise RuntimeError(f"Failed to retrieve updated recipe: {recipe_id}")

            return updated_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating recipe {recipe.id}: {e}", exc_info=True)
            raise

    async def _delete_old_relationships(self, recipe_id: int) -> None:
        """Delete old relationships before update."""
        await self._ingredient_repo.delete_all(recipe_id)
        await self._step_repo.delete_all(recipe_id)
        await self._meal_type_repo.delete_all(recipe_id)
        await self._tag_repo.delete_associations(recipe_id)

    async def _create_new_relationships(self, recipe_id: int, recipe: Recipe) -> None:
        """Create new relationships after update."""
        await self._ingredient_repo.create_all(recipe_id, recipe.ingredients)
        await self._step_repo.create_all(recipe_id, recipe.steps)
        await self._tag_repo.associate_tags(recipe_id, list(recipe.tags))
        await self._meal_type_repo.create_all(recipe_id, list(recipe.meal_types))

    def _apply_relationship_loading(self, query):
        """Apply eager loading for relationships."""
        return query.options(
            selectinload(RecipeModel.ingredients),
            selectinload(RecipeModel.steps),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.meal_types),
        )

    def _should_apply_join(self, join) -> bool:
        """Check if join should be applied (not a relationship)."""
        relationship_attrs = [
            RecipeModel.ingredients,
            RecipeModel.steps,
            RecipeModel.tags,
            RecipeModel.meal_types,
        ]
        return join not in relationship_attrs

    async def _count_results(self, spec: Specification, joins) -> int:
        """Count total results for specification."""
        count_query = select(func.count()).select_from(RecipeModel)

        for join in joins:
            if self._should_apply_join(join):
                count_query = count_query.join(join)

        count_query = count_query.where(spec.to_sql_condition())

        result = await self.session.execute(count_query)
        return result.scalar() or 0

    def _apply_sorting(self, query, page_request: PaginationParams):
        """Apply sorting to query."""
        sort_column = self._get_sort_column(page_request.sort_by or "created_at")

        if page_request.sort_dir == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        return query.order_by(sort_column)

    def _apply_pagination(self, query, page_request: PaginationParams):
        """Apply pagination to query."""
        offset = (page_request.page - 1) * page_request.size
        return query.offset(offset).limit(page_request.size)

    def _get_sort_column(self, sort_by: str):
        """Get SQLAlchemy column for sorting."""
        sort_columns = {
            "created_at": RecipeModel.created_at,
            "updated_at": RecipeModel.updated_at,
            "name": RecipeModel.name,
            # "rating": (RecipeModel.rating_sum / RecipeModel.rating_count),
            "views": RecipeModel.view_count,
            # "favorites": RecipeModel.favorite_count,
        }
        return sort_columns.get(sort_by, RecipeModel.created_at)


class _MealTypeRepository:
    """Internal repository for meal type management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> List[MealType]:
        """List all distinct meal types used in recipes."""
        stmt = select(RecipeMealTypeModel.meal_type).distinct()
        result = await self.session.execute(stmt)
        meal_type_rows = result.scalars().all()
        return [MealType(mt) for mt in meal_type_rows]

    async def delete_all(self, recipe_id: int) -> None:
        """Delete all meal types for a recipe."""
        stmt = delete(RecipeMealTypeModel).where(
            RecipeMealTypeModel.recipe_id == recipe_id
        )
        await self.session.execute(stmt)

    async def create_all(self, recipe_id: int, meal_types: List[MealType]) -> None:
        """Bulk create meal types for a recipe."""
        if not meal_types:
            return

        meal_type_models = [
            RecipeMealTypeModel(
                recipe_id=recipe_id,
                meal_type=mt.value if isinstance(mt, MealType) else mt,
            )
            for mt in meal_types
        ]

        if meal_type_models:
            self.session.add_all(meal_type_models)
            await self.session.flush()


class _IngredientRepository:
    """Internal repository for ingredient management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_all(self, recipe_id: int) -> None:
        """Delete all ingredients for a recipe."""
        stmt = delete(IngredientModel).where(IngredientModel.recipe_id == recipe_id)
        await self.session.execute(stmt)

    async def create_all(self, recipe_id: int, ingredients: List[Ingredient]) -> None:
        """Bulk create ingredients for a recipe."""
        if not ingredients:
            return

        ingredient_models = [
            IngredientModel(
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
            for ing in ingredients
        ]

        if ingredient_models:
            self.session.add_all(ingredient_models)
            await self.session.flush()


class _StepRepository:
    """Internal repository for step management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_all(self, recipe_id: int, steps: List[Step]) -> None:
        """Bulk create steps for a recipe."""
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

    async def delete_all(self, recipe_id: int) -> None:
        """Delete all steps for a recipe."""
        stmt = delete(StepModel).where(StepModel.recipe_id == recipe_id)
        await self.session.execute(stmt)


class _TagRepository:
    """Internal repository for tag management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def associate_tags(self, recipe_id: int, tags: List[Tag]) -> None:
        """Associate tags with recipe (create tags if needed)."""
        if not tags:
            return

        for tag in tags:
            tag_model = await self._get_or_create_tag(tag)

            check_stmt = select(recipe_tags).where(
                and_(
                    recipe_tags.c.recipe_id == recipe_id,
                    recipe_tags.c.tag_id == tag_model.id,
                )
            )
            result = await self.session.execute(check_stmt)

            if result.first() is None:
                stmt = recipe_tags.insert().values(
                    recipe_id=recipe_id, tag_id=tag_model.id
                )
                await self.session.execute(stmt)

        await self.session.flush()

    async def _get_or_create_tag(self, tag: Tag) -> TagModel:
        """Get existing tag or create new one."""
        stmt = select(TagModel).where(TagModel.name == tag.name)
        result = await self.session.execute(stmt)
        tag_model = result.scalar_one_or_none()

        if not tag_model:
            tag_model = TagModel(name=tag.name, description=tag.description)
            self.session.add(tag_model)
            await self.session.flush()

        return tag_model

    async def delete_associations(self, recipe_id: int) -> None:
        """Delete all tag associations for a recipe."""
        stmt = delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        await self.session.execute(stmt)


class SqlAlchemyRecipeFavoriteRepository(RecipeFavoriteRepository):
    """Repository for recipe favorite operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_recipe(self, recipe_id: int) -> int:
        """Count favorites for a recipe."""
        stmt = (
            select(func.count())
            .select_from(recipe_favorites)
            .where(recipe_favorites.c.recipe_id == recipe_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def toggle(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """
        Toggle favorite status.

        Returns:
            True if favorite was added, False if removed
        """
        is_favorite = await self.exists(recipe_id, user_id)

        if is_favorite:
            await self._remove(recipe_id, user_id)
            return False
        else:
            await self._add(recipe_id, user_id)
            return True

    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """Check if recipe is favorited by user."""
        stmt = select(
            select(recipe_favorites.c.recipe_id)
            .where(
                and_(
                    recipe_favorites.c.recipe_id == recipe_id.value,
                    recipe_favorites.c.user_id == user_id.value,
                )
            )
            .exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def _add(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Add favorite."""
        stmt = recipe_favorites.insert().values(
            recipe_id=recipe_id.value,
            user_id=user_id.value,
            created_at=datetime.now(timezone.utc),
        )
        await self.session.execute(stmt)

    async def _remove(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Remove favorite."""
        stmt = delete(recipe_favorites).where(
            and_(
                recipe_favorites.c.recipe_id == recipe_id.value,
                recipe_favorites.c.user_id == user_id.value,
            )
        )
        await self.session.execute(stmt)


class SqlAlchemyRecipeReviewRepository(RecipeReviewRepository):
    """Repository for recipe review operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, recipe_id: RecipeId, user_id: UserId) -> bool:
        """Check if review exists for recipe by user."""
        stmt = select(
            select(recipe_reviews.c.recipe_id)
            .where(
                and_(
                    recipe_reviews.c.recipe_id == recipe_id.value,
                    recipe_reviews.c.user_id == user_id.value,
                )
            )
            .exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def count_by_recipe(self, recipe_id: int) -> int:
        """Count reviews for a recipe."""
        stmt = (
            select(func.count())
            .select_from(recipe_reviews)
            .where(recipe_reviews.c.recipe_id == recipe_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def save(self, review: Review) -> None:
        """
        Create or update a review.

        Args:
            recipe_id: Recipe identifier
            user_id: User identifier
            rating: Rating value
            comment: Optional review comment
        """
        existing_review = await self._find_by_recipe_and_user(
            review.recipe_id.value, review.user_id.value
        )

        if existing_review:
            await self._update(
                existing_review.id,
                existing_review.user_id.value,
                review.rating,
                review.comment,
            )
        else:
            await self._create(
                review.recipe_id.value,
                review.user_id.value,
                review.rating,
                review.comment,
            )

        await self.session.flush()

    async def _find_by_recipe_and_user(self, recipe_id: int, user_id: int):
        """Find existing review."""
        stmt = select(recipe_reviews).where(
            and_(
                recipe_reviews.c.recipe_id == recipe_id,
                recipe_reviews.c.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.first()

    async def delete(self, recipe_id: RecipeId, user_id: UserId) -> None:
        """Delete a review."""
        stmt = delete(recipe_reviews).where(
            and_(
                recipe_reviews.c.recipe_id == recipe_id.value,
                recipe_reviews.c.user_id == user_id.value,
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def _create(
        self, recipe_id: int, user_id: int, rating: int, comment: Optional[str]
    ) -> None:
        """Create new review."""
        stmt = recipe_reviews.insert().values(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        await self.session.execute(stmt)

    async def _update(
        self, recipe_id: int, user_id: int, rating: int, comment: Optional[str]
    ) -> None:
        """Update existing review."""
        stmt = (
            update(recipe_reviews)
            .where(
                and_(
                    recipe_reviews.c.recipe_id == recipe_id,
                    recipe_reviews.c.user_id == user_id,
                )
            )
            .values(
                rating=rating,
                comment=comment,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
