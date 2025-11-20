"""
Internal repository for step management.

Handles recipe step operations as part of the recipe aggregate,
including creating and deleting preparation steps.
"""

import logging
from typing import List
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recipe.domain.models.entities.recipe import Step
from app.modules.recipe.infrastructure.persistence.models import StepModel
from ..base import BaseRepository

logger = logging.getLogger(__name__)


class StepRepository(BaseRepository):
    """
    Internal repository for step management.

    Handles the one-to-many relationship between recipes and preparation steps,
    including step ordering, descriptions, and cooking techniques.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_all(self, recipe_id: int, steps: List[Step]) -> None:
        """
        Bulk create steps for a recipe.

        Args:
            recipe_id: ID of the recipe to associate steps with
            steps: List of step entities to create, ordered by step number

        Note:
            Steps should be provided in the correct order (step_number)
            as this determines the preparation sequence
        """
        if not steps:
            logger.debug(f"No steps to create for recipe {recipe_id}")
            return

        logger.debug(f"Creating {len(steps)} steps for recipe {recipe_id}")

        step_models = []
        for step in steps:
            try:
                step_model = StepModel(
                    recipe_id=recipe_id,
                    step_number=step.number,
                    description=step.description,
                    duration_minutes=step.duration_minutes,
                    technique=step.technique,
                    temperature=step.temperature,
                )
                step_models.append(step_model)

            except Exception as e:
                logger.error(f"Error processing step {step.number}: {e}")
                continue

        if step_models:
            self.session.add_all(step_models)
            await self.session.flush()
            logger.debug(f"Successfully created {len(step_models)} steps")
        else:
            logger.warning("No valid step models were created")

    async def delete_all(self, recipe_id: int) -> None:
        """
        Delete all steps for a specific recipe.

        Args:
            recipe_id: ID of the recipe to clear steps for

        Note:
            This is typically used during recipe updates to remove old steps
        """
        logger.debug(f"Deleting all steps for recipe {recipe_id}")

        stmt = delete(StepModel).where(StepModel.recipe_id == recipe_id)
        await self.session.execute(stmt)
        logger.debug(f"Successfully deleted steps for recipe {recipe_id}")
