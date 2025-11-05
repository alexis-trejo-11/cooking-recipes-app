from typing import Optional


class RecipeValidationException(Exception):
    """Exception raised for errors in the recipe validation."""

    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code
