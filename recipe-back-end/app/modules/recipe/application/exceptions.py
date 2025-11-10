from typing import Any, Dict
from app.utils.core.exceptions.modules import RecipeException
from app.utils.core.exceptions.base import NotFoundException
from app.modules.recipe.domain.models.entities.recipe import RecipeId


class RecipeNotFoundException(NotFoundException):
    """Recipe not found errors"""

    def __init__(
        self,
        recipe_id: RecipeId,
    ):
        super().__init__(
            f"Recipe with ID '{recipe_id}' not found.", "NOT_FOUND", 404, {}, {}
        )


class RecipeDomainException(RecipeException):
    """Base exception for recipe domain errors"""

    pass


class RecipeValidationException(RecipeException):
    """Recipe validation errors"""

    pass


class RecipeAlreadyExistsException(RecipeException):
    """Recipe already exists errors"""

    pass


class InvalidRecipeDataException(RecipeException):
    """Invalid recipe data errors"""

    pass
