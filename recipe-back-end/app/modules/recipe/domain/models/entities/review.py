from dataclasses import dataclass
from .recipe import RecipeId, UserId
from ...exceptions import RecipeReviewException


@dataclass(frozen=True)
class Review:
    recipe_id: RecipeId
    user_id: UserId
    rating: int
    comment: str = ""

    def __eq__(self, other):
        if not isinstance(other, Review):
            return NotImplemented
        return self.rating == other.rating and self.comment == other.comment

    def __post_init__(self):
        if not (1 <= self.rating <= 5):
            raise RecipeReviewException(message="Rating must be between 1 and 5")

        if not isinstance(self.comment, str):
            raise RecipeReviewException(message="Comment must be a string")

        if len(self.comment) > 1000:
            raise RecipeReviewException(
                message="Comment must not exceed 1000 characters"
            )
