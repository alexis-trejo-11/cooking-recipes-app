from .base import *
from .recipe.search_recipes import SearchRecipesUseCaseImpl
from .recipe.get_recipe import GetRecipeUseCaseImpl
from .recipe.create_recipe import CreateRecipeUseCaseImpl
from .recipe.update_recipe import UpdateRecipeUseCaseImpl
from .recipe.delete_recipe import DeleteRecipeUseCaseImpl, RestoreRecipeUseCaseImpl
from .recipe.user_recipes import GetUserRecipesUseCaseImpl
from .recipe.featured_recipes import GetFeaturedRecipesUseCaseImpl
from .recipe.increment_views import IncrementViewCountUseCaseImpl
from .favorites.user_favorites import (
    GetUserFavoritesRecipesUseCaseImpl,
    GetRecipeFavoritesByUserUseCaseImpl,
)
from .favorites.toggle_favorite import ToggleFavoriteUseCaseImpl, IsFavoriteUseCaseImpl
from .review.create_review import CreateReviewUseCaseImpl
from .review.delete_review import DeleteReviewUseCaseImpl

__all__ = [
    # Base interfaces
    "SearchRecipesUseCase",
    "GetFeaturedRecipesUseCase",
    "GetUserRecipesUseCase",
    "GetUserFavoritesRecipesUseCase",
    "GetRecipeUseCase",
    "CreateRecipeUseCase",
    "UpdateRecipeUseCase",
    "RestoreRecipeUseCase",
    "DeleteRecipeUseCase",
    "CreateReviewUseCase",
    "DeleteReviewUseCase",
    "IncrementViewCountUseCase",
    "ToggleFavoriteUseCase",
    "IsFavoriteUseCase",
    "GetRecipeFavoritesByUserUseCase",
    # Implementations
    "SearchRecipesUseCaseImpl",
    "GetRecipeUseCaseImpl",
    "CreateRecipeUseCaseImpl",
    "UpdateRecipeUseCaseImpl",
    "DeleteRecipeUseCaseImpl",
    "RestoreRecipeUseCaseImpl",
    "GetUserRecipesUseCaseImpl",
    "GetFeaturedRecipesUseCaseImpl",
    "IncrementViewCountUseCaseImpl",
    "GetUserFavoritesRecipesUseCaseImpl",
    "GetRecipeFavoritesByUserUseCaseImpl",
    "ToggleFavoriteUseCaseImpl",
    "IsFavoriteUseCaseImpl",
    "CreateReviewUseCaseImpl",
    "DeleteReviewUseCaseImpl",
]
