"""
Dependency injection configuration for Recipe module.

This module provides all dependencies needed for recipe use cases,
repositories, and other components. It follows the dependency inversion
principle and ensures proper resource management.
"""

from typing import AsyncGenerator, Optional
from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from app.config.sql_session import get_db_session
from app.modules.recipe.infrastructure.persistence.repository import (
    SqlAlchemyRecipeRepository,
    SqlAlchemyRecipeReviewRepository,
    SqlAlchemyRecipeFavoriteRepository,
)
from app.modules.recipe.domain.interfaces import (
    RecipeRepository,
    RecipeReviewRepository,
    RecipeFavoriteRepository,
)
from app.modules.recipe.application.use_cases import (
    # Interfaces
    GetRecipeUseCase,
    SearchRecipesUseCase,
    GetUserRecipesUseCase,
    GetFeaturedRecipesUseCase,
    CreateRecipeUseCase,
    UpdateRecipeUseCase,
    RestoreRecipeUseCase,
    DeleteRecipeUseCase,
    DeleteRecipeUseCaseImpl,
    RestoreRecipeUseCaseImpl,
    IncrementViewCountUseCase,
    # Review Use Cases
    CreateReviewUseCase,
    GetRecipeReviewsUseCase,
    GetUserReviewForRecipeUseCase,
    DeleteReviewUseCase,
    UpdateReviewUseCase,
    # Favorites Use Cases
    ToggleFavoriteUseCase,
    GetRecipeFavoritesByUserUseCase,
    GetUserFavoritesRecipesUseCase,
    # Implementations
    # Recipe Use Cases
    GetUserRecipesUseCaseImpl,
    SearchRecipesUseCaseImpl,
    GetRecipeUseCaseImpl,
    GetFeaturedRecipesUseCaseImpl,
    IncrementViewCountUseCaseImpl,
    CreateRecipeUseCaseImpl,
    UpdateRecipeUseCaseImpl,
    # Favorites Use Cases
    IsFavoriteUseCaseImpl,
    GetUserFavoritesRecipesUseCaseImpl,
    GetRecipeFavoritesByUserUseCaseImpl,
    ToggleFavoriteUseCaseImpl,
    # Review Use Cases
    GetUserReviewForRecipeUseCaseImpl,
    GetRecipeReviewsUseCaseImpl,
    CreateReviewUseCaseImpl,
    UpdateReviewUseCaseImpl,
    DeleteReviewUseCaseImpl,
)
from app.modules.recipe.application.dtos import RecipeSearchRequest
from app.modules.auth.presentation.app_depencies import UserRepositoryDep
from app.utils.external.page_request import PydanticPaginationParams as PaginationParams


# Database Session Dependencies
async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for database session.

    Yields:
        AsyncSession: Database session for the request lifecycle

    Ensures:
        Proper cleanup and session closure after request completion
    """
    async for session in get_db_session():
        try:
            yield session
        finally:
            await session.close()


# Repository Dependencies
async def get_recipe_repository(
    session: Annotated[AsyncSession, Depends(get_db_session_dependency)],
) -> RecipeRepository:
    """
    Dependency for RecipeRepository.

    Args:
        session: Database session

    Returns:
        RecipeRepository: SQLAlchemy implementation of recipe repository
    """
    return SqlAlchemyRecipeRepository(session)


async def get_recipe_review_repository(
    session: Annotated[AsyncSession, Depends(get_db_session_dependency)],
) -> RecipeReviewRepository:
    """
    Dependency for RecipeReviewRepository.

    Args:
        session: Database session

    Returns:
        RecipeReviewRepository: SQLAlchemy implementation of review repository
    """
    return SqlAlchemyRecipeReviewRepository(session)


async def get_recipe_favorite_repository(
    session: Annotated[AsyncSession, Depends(get_db_session_dependency)],
) -> RecipeFavoriteRepository:
    """
    Dependency for RecipeFavoriteRepository.

    Args:
        session: Database session

    Returns:
        RecipeFavoriteRepository: SQLAlchemy implementation of favorite repository
    """
    return SqlAlchemyRecipeFavoriteRepository(session)


# Use Case Dependencies - Recipe Operations
async def get_create_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    user_repository: UserRepositoryDep,
) -> CreateRecipeUseCase:
    """
    Dependency for CreateRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        user_repository: Repository for user validation

    Returns:
        CreateRecipeUseCase: Use case for creating recipes
    """
    return CreateRecipeUseCaseImpl(recipe_repository, user_repository)


async def get_get_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetRecipeUseCase:
    """
    Dependency for GetRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        GetRecipeUseCase: Use case for retrieving recipes
    """
    return GetRecipeUseCaseImpl(recipe_repository)


async def get_update_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> UpdateRecipeUseCase:
    """
    Dependency for UpdateRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        UpdateRecipeUseCase: Use case for updating recipes
    """
    return UpdateRecipeUseCaseImpl(recipe_repository)


async def get_delete_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> DeleteRecipeUseCase:
    """
    Dependency for DeleteRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        DeleteRecipeUseCase: Use case for deleting recipes
    """
    return DeleteRecipeUseCaseImpl(recipe_repository)


async def get_restore_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> RestoreRecipeUseCase:
    """
    Dependency for RestoreRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        RestoreRecipeUseCase: Use case for restoring soft-deleted recipes
    """
    return RestoreRecipeUseCaseImpl(recipe_repository)


# Use Case Dependencies - Search & Listing
async def get_search_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> SearchRecipesUseCase:
    """
    Dependency for SearchRecipesUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        SearchRecipesUseCase: Use case for searching recipes with filters
    """
    return SearchRecipesUseCaseImpl(recipe_repository)


async def get_get_user_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetUserRecipesUseCase:
    """
    Dependency for GetUserRecipesUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        GetUserRecipesUseCase: Use case for retrieving user's recipes
    """
    return GetUserRecipesUseCaseImpl(recipe_repository)


async def get_get_featured_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetFeaturedRecipesUseCase:
    """
    Dependency for GetFeaturedRecipesUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        GetFeaturedRecipesUseCase: Use case for retrieving featured recipes
    """
    return GetFeaturedRecipesUseCaseImpl(recipe_repository)


# Use Case Dependencies - Favorites
async def get_toggle_favorite_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    recipe_favorite_repository: Annotated[
        RecipeFavoriteRepository, Depends(get_recipe_favorite_repository)
    ],
) -> ToggleFavoriteUseCase:
    """
    Dependency for ToggleFavoriteUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        recipe_favorite_repository: Repository for favorite operations

    Returns:
        ToggleFavoriteUseCase: Use case for toggling favorite status
    """
    return ToggleFavoriteUseCaseImpl(recipe_repository, recipe_favorite_repository)


async def get_is_favorite_use_case(
    recipe_favorite_repository: Annotated[
        RecipeFavoriteRepository, Depends(get_recipe_favorite_repository)
    ],
) -> IsFavoriteUseCaseImpl:
    """
    Dependency for IsFavoriteUseCase.

    Args:
        recipe_favorite_repository: Repository for favorite operations

    Returns:
        IsFavoriteUseCaseImpl: Use case for checking favorite status
    """
    return IsFavoriteUseCaseImpl(recipe_favorite_repository=recipe_favorite_repository)


async def get_get_user_favorite_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetUserFavoritesRecipesUseCase:
    """
    Dependency for GetUserFavoritesRecipesUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        GetUserFavoritesRecipesUseCase: Use case for retrieving user's favorite recipes
    """
    return GetUserFavoritesRecipesUseCaseImpl(recipe_repository)


async def get_get_recipe_favorites_by_user_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetRecipeFavoritesByUserUseCase:
    """
    Dependency for GetRecipeFavoritesByUserUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        GetRecipeFavoritesByUserUseCase: Use case for retrieving user's favorite recipes
    """
    return GetRecipeFavoritesByUserUseCaseImpl(recipe_repository)


# Use Case Dependencies - Reviews
async def get_get_user_review_for_recipe_use_case(
    recipe_review_repository: Annotated[
        RecipeReviewRepository, Depends(get_recipe_review_repository)
    ],
) -> GetUserReviewForRecipeUseCase:
    """
    Dependency for GetUserReviewForRecipeUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        recipe_review_repository: Repository for review operations

    Returns:
        GetUserReviewForRecipeUseCase: Use case for retrieving user's review for a recipe
    """
    return GetUserReviewForRecipeUseCaseImpl(recipe_review_repository)


async def get_get_recipe_reviews_use_case(
    recipe_review_repository: Annotated[
        RecipeReviewRepository, Depends(get_recipe_review_repository)
    ],
) -> GetRecipeReviewsUseCase:
    """
    Dependency for GetRecipeReviewsUseCase.

    Args:
        recipe_review_repository: Repository for review operations

    Returns:
        GetRecipeReviewsUseCase: Use case for retrieving reviews for a recipe
    """
    return GetRecipeReviewsUseCaseImpl(recipe_review_repository)


async def get_create_review_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    recipe_review_repository: Annotated[
        RecipeReviewRepository, Depends(get_recipe_review_repository)
    ],
) -> CreateReviewUseCase:
    """
    Dependency for CreateReviewUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        recipe_review_repository: Repository for review operations

    Returns:
        CreateReviewUseCase: Use case for creating reviews
    """
    return CreateReviewUseCaseImpl(recipe_repository, recipe_review_repository)


async def get_update_review_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    recipe_review_repository: Annotated[
        RecipeReviewRepository, Depends(get_recipe_review_repository)
    ],
) -> UpdateReviewUseCase:
    """
    Dependency for UpdateReviewUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        recipe_review_repository: Repository for review operations

    Returns:
        UpdateReviewUseCase: Use case for updating reviews
    """
    return UpdateReviewUseCaseImpl(recipe_repository, recipe_review_repository)


async def get_delete_review_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    recipe_review_repository: Annotated[
        RecipeReviewRepository, Depends(get_recipe_review_repository)
    ],
) -> DeleteReviewUseCase:
    """
    Dependency for DeleteReviewUseCase.

    Args:
        recipe_repository: Repository for recipe operations
        recipe_review_repository: Repository for review operations

    Returns:
        DeleteReviewUseCase: Use case for deleting reviews
    """
    return DeleteReviewUseCaseImpl(recipe_repository, recipe_review_repository)


# Use Case Dependencies - Analytics
async def get_increment_view_count_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> IncrementViewCountUseCase:
    """
    Dependency for IncrementViewCountUseCase.

    Args:
        recipe_repository: Repository for recipe operations

    Returns:
        IncrementViewCountUseCase: Use case for incrementing view counts
    """
    return IncrementViewCountUseCaseImpl(recipe_repository)


# Request Parameter Dependencies
def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    sort_dir: str = Query(
        "asc", regex="^(asc|desc)$", description="Sort direction: 'asc' or 'desc'"
    ),
    sort_by: str = Query("created_at", description="Field to sort by"),
) -> PaginationParams:
    """
    Dependency for pagination parameters.

    Args:
        page: Page number (default: 1)
        size: Page size (default: 10, max: 100)
        sort_dir: Sort direction (default: 'asc')
        sort_by: Sort field (default: 'created_at')

    Returns:
        PaginationParams: Validated pagination parameters
    """
    return PaginationParams(page=page, size=size, sort_dir=sort_dir, sort_by=sort_by)


def get_recipe_search_request(
    pagination: PaginationParams = Depends(get_pagination_params),
    name: Optional[str] = Query(
        None, min_length=1, max_length=200, description="Recipe name filter"
    ),
    author_id: Optional[int] = Query(None, ge=1, description="Filter by author ID"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine type"),
    meal_types: Optional[set[str]] = Query(None, description="Filter by meal types"),
    tags: Optional[set[str]] = Query(None, description="Filter by tags"),
    ingredient_name: Optional[str] = Query(
        None, description="Filter by ingredient name"
    ),
    max_cook_time: Optional[int] = Query(
        None, ge=0, description="Maximum cooking time in minutes"
    ),
    min_rating: Optional[float] = Query(
        None, ge=0.0, le=5.0, description="Minimum rating (0.0-5.0)"
    ),
) -> RecipeSearchRequest:
    """
    Dependency for RecipeSearchRequest with comprehensive filtering.

    Args:
        pagination: Pagination parameters
        name: Filter by recipe name
        author_id: Filter by author
        difficulty: Filter by difficulty level
        cuisine: Filter by cuisine type
        meal_types: Filter by meal types
        tags: Filter by tags
        ingredient_name: Filter by ingredient
        max_cook_time: Filter by maximum cooking time
        min_rating: Filter by minimum rating

    Returns:
        RecipeSearchRequest: Validated search request with filters
    """
    return RecipeSearchRequest(
        name=name,
        author_id=author_id,
        difficulty=difficulty,
        cuisine=cuisine,
        meal_types=list(meal_types) if meal_types else None,
        ingredient_name=ingredient_name,
        max_cooking_time=max_cook_time,
        include_deleted=False,  # Security: never include deleted recipes in public search
        tags=list(tags) if tags else None,
        min_rating=min_rating,
        pagination=pagination,
    )


# Dependency Type Annotations for FastAPI
# Command Use Cases (write operations)
CreateRecipeUseCaseDep = Annotated[
    CreateRecipeUseCase, Depends(get_create_recipe_use_case)
]
UpdateRecipeUseCaseDep = Annotated[
    UpdateRecipeUseCase, Depends(get_update_recipe_use_case)
]
DeleteRecipeUseCaseDep = Annotated[
    DeleteRecipeUseCase, Depends(get_delete_recipe_use_case)
]
RestoreRecipeUseCaseDep = Annotated[
    RestoreRecipeUseCase, Depends(get_restore_recipe_use_case)
]
CreateReviewUseCaseDep = Annotated[
    CreateReviewUseCase, Depends(get_create_review_use_case)
]
UpdateReviewUseCaseDep = Annotated[
    UpdateReviewUseCase, Depends(get_update_review_use_case)
]
DeleteReviewUseCaseDep = Annotated[
    DeleteReviewUseCase, Depends(get_delete_review_use_case)
]
ToggleFavoriteUseCaseDep = Annotated[
    ToggleFavoriteUseCase, Depends(get_toggle_favorite_use_case)
]
IncrementViewCountUseCaseDep = Annotated[
    IncrementViewCountUseCase, Depends(get_increment_view_count_use_case)
]

# Query Use Cases (read operations)
GetRecipeUseCaseDep = Annotated[GetRecipeUseCase, Depends(get_get_recipe_use_case)]
SearchRecipesUseCaseDep = Annotated[
    SearchRecipesUseCase, Depends(get_search_recipes_use_case)
]
GetUserRecipesUseCaseDep = Annotated[
    GetUserRecipesUseCase, Depends(get_get_user_recipes_use_case)
]
GetFeaturedRecipesUseCaseDep = Annotated[
    GetFeaturedRecipesUseCase, Depends(get_get_featured_recipes_use_case)
]
GetUserFavoritesRecipesUseCaseDep = Annotated[
    GetUserFavoritesRecipesUseCase, Depends(get_get_user_favorite_recipes_use_case)
]
GetRecipeFavoritesByUserUseCaseDep = Annotated[
    GetRecipeFavoritesByUserUseCase, Depends(get_get_recipe_favorites_by_user_use_case)
]
GetUserReviewForRecipeUseCaseDep = Annotated[
    GetUserReviewForRecipeUseCase, Depends(get_get_user_review_for_recipe_use_case)
]
GetRecipeReviewsUseCaseDep = Annotated[
    GetRecipeReviewsUseCase, Depends(get_get_recipe_reviews_use_case)
]
IsFavoriteUseCaseDep = Annotated[
    IsFavoriteUseCaseImpl, Depends(get_is_favorite_use_case)
]

# Common Dependencies
PaginationParamsDep = Annotated[PaginationParams, Depends(get_pagination_params)]
RecipeSearchRequestDep = Annotated[
    RecipeSearchRequest, Depends(get_recipe_search_request)
]
