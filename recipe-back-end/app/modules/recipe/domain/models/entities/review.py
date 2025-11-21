from dataclasses import dataclass
from datetime import datetime, timezone, timezone
from .recipe import RecipeId, UserId
from ...exceptions import RecipeReviewException


@dataclass(frozen=True)
class Review:
    recipe_id: RecipeId
    user_id: UserId
    rating: int
    created_at: datetime
    updated_at: datetime
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

    @staticmethod
    def create(
        recipe_id: RecipeId,
        user_id: UserId,
        rating: int,
        comment: str = "",
    ) -> "Review":
        now = datetime.now(timezone.utc)
        return Review(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=now,
            updated_at=now,
        )

    def update(self, rating: int, comment: str = "") -> "Review":
        now = datetime.now(timezone.utc)
        return Review(
            recipe_id=self.recipe_id,
            user_id=self.user_id,
            rating=rating,
            comment=comment,
            created_at=self.created_at,
            updated_at=now,
        )
