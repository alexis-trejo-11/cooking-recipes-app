"""
SQLAlchemy implementation of RecipeRepository.

Handles all recipe aggregate operations including CRUD, search,
and relationship management.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.core.pagination import Page, PaginationParams
from app.utils.core.specification import Specification
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.auth.domain.user import UserId
from app.modules.recipe.domain.models.entities.recipe import Recipe, RecipeId
from app.modules.recipe.infrastructure.persistence.models import (
    RecipeModel,
    ReviewModel,
    recipe_favorites,
)
from app.modules.recipe.application.exceptions import RecipeNotFoundException
from .base import BaseRepository, QueryBuilderMixin
from .internal.meal_type_repo import MealTypeRepository
from .internal.ingredient_repo import IngredientRepository
from .internal.step_repo import StepRepository
from .internal.tag_repo import TagRepository
from ..mapper import RecipeMapper

logger = logging.getLogger(__name__)


class SqlAlchemyRecipeRepository(RecipeRepository, BaseRepository, QueryBuilderMixin):
    """
    SQLAlchemy implementation of recipe aggregate repository.

    This repository handles the complete recipe aggregate including all
    related entities (ingredients, steps, tags, meal types) and ensures
    data consistency across all operations.
    """

    def __init__(self, session: AsyncSession):
        BaseRepository.__init__(self, session)
        self.mapper = RecipeMapper()
        self._meal_type_repo = MealTypeRepository(session)
        self._ingredient_repo = IngredientRepository(session)
        self._step_repo = StepRepository(session)
        self._tag_repo = TagRepository(session)

    async def find_by_id(
        self,
        recipe_id: RecipeId,
        include_deleted: bool = False,
        with_relations: bool = False,
    ) -> Optional[Recipe]:
        """
        Find recipe by ID with optional relationships and deleted records.

        Args:
            recipe_id: Recipe identifier
            include_deleted: Whether to include soft-deleted recipes
            with_relations: Whether to eagerly load relationships

        Returns:
            Recipe entity if found, None otherwise

        Raises:
            RuntimeError: If recipe retrieval fails after creation/update
        """
        logger.debug(
            f"Finding recipe by ID: {recipe_id}, include_deleted: {include_deleted}"
        )

        stmt = select(RecipeModel).where(RecipeModel.id == recipe_id.value)

        if not include_deleted:
            stmt = stmt.where(RecipeModel.deleted_at.is_(None))

        if with_relations:
            stmt = self._apply_relationship_loading(stmt)

        result = await self.session.execute(stmt)
        recipe_model = result.scalar_one_or_none()

        if not recipe_model:
            return None

        # Calculate aggregates
        rating_stats = await self._get_rating_stats(recipe_id.value)
        favorite_count = await self._get_favorite_count(recipe_id.value)

        return self.mapper.model_to_entity(
            recipe_model, rating_stats["sum"], rating_stats["count"], favorite_count
        )

    async def find_by_id_and_author(
        self, recipe_id: RecipeId, author_id: UserId
    ) -> Optional[Recipe]:
        """
        Find recipe by ID and author for authorization checks.

        Args:
            recipe_id: Recipe identifier
            author_id: Author user identifier

        Returns:
            Recipe entity if found and authorized, None otherwise
        """
        logger.debug(f"Finding recipe {recipe_id} for author {author_id}")

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

    async def find_featured_recipes(self, limit: int = 5) -> List[Recipe]:
        """
        Find featured recipes for homepage display.

        Args:
            limit: Maximum number of recipes to return

        Returns:
            List of featured recipe entities
        """
        logger.debug(f"Finding {limit} featured recipes")

        stmt = (
            select(RecipeModel)
            .where(RecipeModel.deleted_at.is_(None))
            .order_by(RecipeModel.view_count.desc())
            .limit(limit)
        )
        stmt = self._apply_relationship_loading(stmt)

        result = await self.session.execute(stmt)
        recipe_models = result.scalars().all()

        return [self.mapper.model_to_entity(model) for model in recipe_models]

    async def find_favorites_by_user_id(
        self,
        user_id: UserId,
        page_request: PaginationParams,
    ) -> Page[Recipe]:
        """
        Find paginated favorite recipes for a user.

        Args:
            user_id: User identifier
            page_request: Pagination parameters

        Returns:
            Page of recipe entities
        """
        logger.debug(f"Finding favorite recipes for user {user_id}")

        # Subquery for user's favorite recipe IDs
        favorites_subquery = (
            select(recipe_favorites.c.recipe_id)
            .where(recipe_favorites.c.user_id == user_id.value)
            .subquery()
        )

        # Main query with favorites join
        stmt = select(RecipeModel).join(
            favorites_subquery, RecipeModel.id == favorites_subquery.c.recipe_id
        )

        # Count total favorites
        count_stmt = select(func.count()).select_from(favorites_subquery)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        if total == 0:
            return Page.empty()

        # Apply sorting, pagination and relationships
        stmt = self._apply_sorting(stmt, page_request)
        stmt = self._apply_pagination(stmt, page_request)
        stmt = self._apply_relationship_loading(stmt)

        result = await self.session.execute(stmt)
        recipe_models = result.scalars().all()

        recipes = [self.mapper.model_to_entity(model) for model in recipe_models]
        return Page(
            items=recipes,
            total=total,
            page=page_request.page,
            size=page_request.size,
        )

    async def search(
        self, spec: Specification, page_request: PaginationParams
    ) -> Page[Recipe]:
        """
        Search recipes with specification and pagination.

        Args:
            spec: Search specification
            page_request: Pagination parameters

        Returns:
            Page of recipe entities matching the specification

        Raises:
            Exception: If search operation fails
        """
        logger.debug(f"Searching recipes with specification")

        try:
            # Build base query
            query = select(RecipeModel)
            joins = spec.get_joins()

            # Apply joins
            for join in joins:
                if self._should_apply_join(join):
                    query = query.join(join)

            # Apply specification condition
            query = query.where(spec.to_sql_condition())

            # Count total results
            total = await self._count_results(query)

            # Apply sorting, pagination and relationships
            query = self._apply_sorting(query, page_request)
            query = self._apply_pagination(query, page_request)
            query = self._apply_relationship_loading(query)

            # Execute query
            result = await self.session.execute(query)
            recipe_models = result.scalars().all()

            # Map to entities
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
        """
        Check if recipe with name exists for author.

        Args:
            name: Recipe name
            author_id: Author user identifier

        Returns:
            True if recipe exists, False otherwise
        """
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
        """
        Check if recipe exists by ID.

        Args:
            recipe_id: Recipe identifier
            include_deleted: Whether to include soft-deleted recipes

        Returns:
            True if recipe exists, False otherwise
        """
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

        Raises:
            RecipeNotFoundException: If updating non-existent recipe
            RuntimeError: If save operation fails
        """
        if recipe.id and recipe.id.value > 0:
            return await self._update(recipe)
        else:
            return await self._create(recipe)

    async def delete(self, recipe_id: RecipeId) -> bool:
        """
        Soft delete a recipe.

        Args:
            recipe_id: Recipe identifier

        Returns:
            True if recipe was deleted, False if not found
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
        """
        Increment recipe view count.

        Args:
            recipe_id: Recipe identifier

        Raises:
            RecipeNotFoundException: If recipe not found
        """
        logger.debug(f"Incrementing view count for recipe {recipe_id}")

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

        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise RecipeNotFoundException(recipe_id)

        await self.session.commit()

    # Private implementation methods
    async def _create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe with all relationships."""
        try:
            # Create main recipe record
            recipe_data = self.mapper.entity_to_dict(recipe)
            recipe_model = RecipeModel(**recipe_data)
            self.session.add(recipe_model)
            await self.session.flush()

            recipe_id = recipe_model.id

            # Create all relationships
            await self._create_recipe_relationships(recipe_id, recipe)

            await self.session.commit()

            # Retrieve complete recipe
            created_recipe = await self.find_by_id(RecipeId(recipe_id))
            if created_recipe is None:
                raise RuntimeError(f"Failed to retrieve created recipe: {recipe_id}")

            logger.info(f"Successfully created recipe: {recipe_id}")
            return created_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating recipe: {e}", exc_info=True)
            raise

    async def _update(self, recipe: Recipe) -> Recipe:
        """Update existing recipe and its relationships."""
        try:
            if not recipe.id:
                raise RecipeNotFoundException(recipe.id)

            recipe_id = recipe.id.value

            # Update main recipe record
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

            # Update relationships (delete old, create new)
            await self._delete_old_relationships(recipe_id)
            await self._create_recipe_relationships(recipe_id, recipe)

            await self.session.commit()
            self.session.expire_all()

            # Retrieve updated recipe
            updated_recipe = await self.find_by_id(recipe.id, include_deleted=True)
            if updated_recipe is None:
                raise RuntimeError(f"Failed to retrieve updated recipe: {recipe_id}")

            logger.info(f"Successfully updated recipe: {recipe_id}")
            return updated_recipe

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating recipe {recipe.id}: {e}", exc_info=True)
            raise

    async def _create_recipe_relationships(
        self, recipe_id: int, recipe: Recipe
    ) -> None:
        """Create all recipe relationships in bulk."""
        await self._ingredient_repo.create_all(recipe_id, recipe.ingredients)
        await self._step_repo.create_all(recipe_id, recipe.steps)
        await self._tag_repo.associate_tags(recipe_id, list(recipe.tags))
        await self._meal_type_repo.create_all(recipe_id, list(recipe.meal_types))

    async def _delete_old_relationships(self, recipe_id: int) -> None:
        """Delete all old relationships before update."""
        await self._ingredient_repo.delete_all(recipe_id)
        await self._step_repo.delete_all(recipe_id)
        await self._meal_type_repo.delete_all(recipe_id)
        await self._tag_repo.delete_associations(recipe_id)

    async def _get_rating_stats(self, recipe_id: int) -> dict:
        """Get rating statistics for a recipe."""
        rating_count_stmt = (
            select(func.count())
            .select_from(ReviewModel)
            .where(ReviewModel.recipe_id == recipe_id)
        )
        rating_sum_stmt = (
            select(func.coalesce(func.sum(ReviewModel.rating), 0))
            .select_from(ReviewModel)
            .where(ReviewModel.recipe_id == recipe_id)
        )

        rating_count_result = await self.session.execute(rating_count_stmt)
        rating_sum_result = await self.session.execute(rating_sum_stmt)

        return {
            "count": rating_count_result.scalar() or 0,
            "sum": rating_sum_result.scalar() or 0,
        }

    async def _get_favorite_count(self, recipe_id: int) -> int:
        """Get favorite count for a recipe."""
        favorite_count_stmt = (
            select(func.count())
            .select_from(recipe_favorites)
            .where(recipe_favorites.c.recipe_id == recipe_id)
        )
        favorite_count_result = await self.session.execute(favorite_count_stmt)
        return favorite_count_result.scalar() or 0
