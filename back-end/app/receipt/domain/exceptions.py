class RecipeDomainException(Exception):
    """Base exception for all Recipe domain errors"""

    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RecipeValidationException(RecipeDomainException):
    """Raised when recipe data validation fails"""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)


class RecipeNotFoundException(RecipeDomainException):
    """Raised when recipe is not found"""

    def __init__(self, recipe_id: str, error_code: str = "NOT_FOUND"):
        super().__init__(f"Recipe {recipe_id} not found", error_code)


class RecipeDeletedException(RecipeDomainException):
    """Raised when operating on a deleted recipe"""

    def __init__(self, recipe_id: str, error_code: str = "DELETED"):
        super().__init__(
            f"Cannot perform operations on deleted recipe {recipe_id}", error_code
        )


class IngredientException(RecipeDomainException):
    """Base exception for ingredient-related errors"""

    def __init__(self, message: str, error_code: str = "INGREDIENT_ERROR"):
        super().__init__(message, error_code)


class IngredientAlreadyExistsException(IngredientException):
    """Raised when trying to add a duplicate ingredient"""

    def __init__(
        self,
        ingredient_name: str,
        recipe_id: str,
        error_code: str = "INGREDIENT_DUPLICATE",
    ):
        super().__init__(
            f"Ingredient {ingredient_name} already exists in recipe {recipe_id}",
            error_code,
        )


class IngredientNotFoundException(IngredientException):
    """Raised when ingredient is not found"""

    def __init__(
        self,
        ingredient_id: str,
        recipe_id: str,
        error_code: str = "INGREDIENT_NOT_FOUND",
    ):
        super().__init__(
            f"Ingredient {ingredient_id} not found in recipe {recipe_id}", error_code
        )


class StepException(RecipeDomainException):
    """Base exception for step-related errors"""

    def __init__(self, message: str, error_code: str = "STEP_ERROR"):
        super().__init__(message, error_code)


class InvalidStepOrderException(StepException):
    """Raised when step reordering is invalid"""

    def __init__(self, message: str, error_code: str = "INVALID_STEP_ORDER"):
        super().__init__(message, error_code)


class NutritionalInfoException(RecipeDomainException):
    """Base exception for nutritional info errors"""

    def __init__(self, message: str, error_code: str = "NUTRITIONAL_ERROR"):
        super().__init__(message, error_code)


class InvalidQuantityException(NutritionalInfoException):
    """Raised when quantity operations are invalid"""

    def __init__(self, message: str, error_code: str = "INVALID_QUANTITY"):
        super().__init__(message, error_code)


class RecipeStateException(RecipeDomainException):
    """Raised when recipe is in invalid state for operation"""

    def __init__(self, message: str, error_code: str = "INVALID_STATE"):
        super().__init__(message, error_code)


class UnauthorizedAccessException(RecipeDomainException):
    """Raised when user tries to access/modify resource they don't own"""

    def __init__(
        self, user_id: str, resource_id: str, error_code: str = "UNAUTHORIZED_ACCESS"
    ):
        super().__init__(
            f"User {user_id} is not authorized to access resource {resource_id}",
            error_code,
        )


class RecipeAlreadyRatedException(RecipeDomainException):
    """Raised when user tries to rate a recipe they already rated"""

    def __init__(self, user_id: str, recipe_id: str, error_code: str = "ALREADY_RATED"):
        super().__init__(
            f"User {user_id} has already rated recipe {recipe_id}", error_code
        )


class FavoriteAlreadyExistsException(RecipeDomainException):
    """Raised when trying to add duplicate favorite"""

    def __init__(
        self, user_id: str, recipe_id: str, error_code: str = "FAVORITE_EXISTS"
    ):
        super().__init__(
            f"Recipe {recipe_id} is already in user {user_id}'s favorites", error_code
        )


class FavoriteNotFoundException(RecipeDomainException):
    """Raised when favorite not found"""

    def __init__(
        self, user_id: str, recipe_id: str, error_code: str = "FAVORITE_NOT_FOUND"
    ):
        super().__init__(
            f"Recipe {recipe_id} not found in user {user_id}'s favorites", error_code
        )
