# app/modules/recipe/infrastructure/persistence/repositories/internal/tag_repo.py
"""
Internal repository for tag management.

Handles tag operations as part of the recipe aggregate,
including tag creation, association, and management of the
many-to-many relationship between recipes and tags.
"""

import logging
from typing import List
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.domain.models.entities.recipe import Tag
from app.modules.recipe.infrastructure.persistence.models import TagModel, recipe_tags
from ..base import BaseRepository

logger = logging.getLogger(__name__)


class TagRepository(BaseRepository):
    """
    Internal repository for tag management.

    Handles the many-to-many relationship between recipes and tags,
    including tag creation, lookup, and association management.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def associate_tags(self, recipe_id: int, tags: List[Tag]) -> None:
        """
        Associate tags with a recipe, creating tags if they don't exist.

        Args:
            recipe_id: ID of the recipe to associate tags with
            tags: List of tag entities to associate

        Note:
            This method handles both tag creation and association:
            1. Creates tags that don't exist in the database
            2. Associates existing or new tags with the recipe
            3. Avoids duplicate associations
        """
        if not tags:
            logger.debug(f"No tags to associate with recipe {recipe_id}")
            return

        logger.debug(f"Associating {len(tags)} tags with recipe {recipe_id}")

        tags_associated = 0
        for tag in tags:
            try:
                # Get or create the tag
                tag_model = await self._get_or_create_tag(tag)

                # Check if association already exists
                association_exists = await self._check_association_exists(
                    recipe_id, tag_model.id
                )

                if not association_exists:
                    # Create new association
                    await self._create_association(recipe_id, tag_model.id)
                    tags_associated += 1

            except Exception as e:
                logger.error(f"Error associating tag '{tag.name}': {e}")
                continue

        await self.session.flush()
        logger.debug(
            f"Successfully associated {tags_associated} tags with recipe {recipe_id}"
        )

    async def delete_associations(self, recipe_id: int) -> None:
        """
        Delete all tag associations for a specific recipe.

        Args:
            recipe_id: ID of the recipe to clear tag associations for

        Note:
            This only removes the associations, not the tags themselves.
            Tags remain in the database for potential reuse.
        """
        logger.debug(f"Deleting all tag associations for recipe {recipe_id}")

        stmt = delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        await self.session.execute(stmt)
        logger.debug(f"Successfully deleted tag associations for recipe {recipe_id}")

    async def _get_or_create_tag(self, tag: Tag) -> TagModel:
        """
        Get existing tag or create new one.

        Args:
            tag: Tag entity to find or create

        Returns:
            TagModel instance (either existing or newly created)
        """
        # Try to find existing tag
        stmt = select(TagModel).where(TagModel.name == tag.name)
        result = await self.session.execute(stmt)
        tag_model = result.scalar_one_or_none()

        if tag_model:
            logger.debug(f"Found existing tag: {tag.name}")
            return tag_model

        # Create new tag
        logger.debug(f"Creating new tag: {tag.name}")
        tag_model = TagModel(name=tag.name, description=tag.description)
        self.session.add(tag_model)
        await self.session.flush()

        return tag_model

    async def _check_association_exists(self, recipe_id: int, tag_id: int) -> bool:
        """
        Check if a tag-recipe association already exists.

        Args:
            recipe_id: Recipe ID
            tag_id: Tag ID

        Returns:
            True if association exists, False otherwise
        """
        stmt = select(recipe_tags).where(
            and_(
                recipe_tags.c.recipe_id == recipe_id,
                recipe_tags.c.tag_id == tag_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def _create_association(self, recipe_id: int, tag_id: int) -> None:
        """
        Create a new tag-recipe association.

        Args:
            recipe_id: Recipe ID
            tag_id: Tag ID
        """
        stmt = recipe_tags.insert().values(recipe_id=recipe_id, tag_id=tag_id)
        await self.session.execute(stmt)
        logger.debug(f"Created association: recipe {recipe_id} -> tag {tag_id}")
