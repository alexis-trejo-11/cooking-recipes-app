from typing import Any, Dict
from app.utils.core.exceptions.modules import RecipeException
from app.utils.core.exceptions.base import NotFoundException
from app.modules.recipe.domain.models.entities.recipe import RecipeId
from app.modules.auth.application.exceptions import UserNotFoundException


class RecipeNotFoundException(NotFoundException):
    """Recipe not found errors"""

    def __init__(
        self,
        recipe_id: RecipeId,
    ):
        super().__init__(
            f"Recipe with ID '{recipe_id}' not found.", "NOT_FOUND", 404, {}, {}
        )


class ReviewDontFoundException(NotFoundException):
    """Review not found errors"""

    def __init__(self, recipe_id: RecipeId, user_id):
        super().__init__(
            f"Review for Recipe with ID '{recipe_id}' by User with ID '{str(user_id)}' not found.",
            "NOT_FOUND",
            404,
            {},
            {},
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
