# app/modules/recipe/presentation/controllers/recipe_controller.py
"""
Recipe Controller

This module contains all API endpoints for recipe operations including:
- CRUD operations for recipes
- Search and filtering
- Favorite management
- Review management
- Analytics (views)

All endpoints include proper authentication, rate limiting, and validation.
"""

from fastapi import APIRouter, status, Path, HTTPException, Depends
from typing import List

from app.modules.auth.presentation.auth_depencies import get_current_user
from app.modules.auth.domain.user import User
from app.modules.recipe.application.dtos import *
from app.modules.recipe.application.exceptions import (
    RecipeNotFoundException,
    RecipeValidationException,
    UserNotFoundException,
)
from app.modules.recipe.presentation.dependencies import (
    # Command Use Cases
    # Recipe Use Cases
    CreateRecipeUseCaseDep,
    IncrementViewCountUseCaseDep,
    UpdateRecipeUseCaseDep,
    DeleteRecipeUseCaseDep,
    RestoreRecipeUseCaseDep,
    # Review Use Cases
    CreateReviewUseCaseDep,
    UpdateReviewUseCaseDep,
    DeleteReviewUseCaseDep,
    # Favorite Use Cases
    ToggleFavoriteUseCaseDep,
    # Query Use Cases
    # Recipe Use Cases
    GetRecipeUseCaseDep,
    SearchRecipesUseCaseDep,
    GetUserRecipesUseCaseDep,
    GetFeaturedRecipesUseCaseDep,
    # Favorite Use Cases
    GetUserFavoritesRecipesUseCaseDep,
    GetRecipeFavoritesByUserUseCaseDep,
    IsFavoriteUseCaseDep,
    # Review Use Cases
    GetRecipeReviewsUseCaseDep,
    GetUserReviewForRecipeUseCaseDep,
    # Request Dependencies
    PaginationParamsDep,
    RecipeSearchRequestDep,
)
from app.config.rate_limiter import rate_limit
from app.modules.recipe.domain.models.entities.recipe import RecipeId

# Router configuration
router = APIRouter(
    prefix="/api/v1/recipes",
    tags=["Recipes"],
    responses={
        404: {"description": "Recipe not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Too many requests"},
    },
)


@router.get(
    "/featured",
    response_model=List[RecipeSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Featured Recipes",
    description="Retrieve a curated list of featured recipes for the homepage",
    response_description="List of featured recipes",
)
@rate_limit("public")
async def get_featured_recipes(
    use_case: GetFeaturedRecipesUseCaseDep,
) -> List[RecipeSummaryResponse]:
    """
    Get featured recipes.

    Returns a list of recipes selected by editors for featuring on the homepage.
    Typically includes 3-5 high-quality, popular, or seasonal recipes.

    Returns:
        List[RecipeSummaryResponse]: Featured recipes with basic information
    """
    return await use_case.execute()


@router.get(
    "",
    response_model=RecipePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Recipes",
    description="Search recipes with advanced filtering and pagination",
    response_description="Paginated search results",
)
@rate_limit("public")
async def search_recipes(
    use_case: SearchRecipesUseCaseDep,
    request: RecipeSearchRequestDep,
) -> RecipePageResponse:
    """
    Search recipes with comprehensive filters.

    Advanced search functionality supporting multiple filters:
    - Text search in recipe names
    - Filter by author, difficulty, cuisine
    - Filter by meal types, tags, ingredients
    - Filter by cooking time and reviews
    - Full pagination support

    Args:
        request: Search criteria including filters and pagination

    Returns:
        RecipePageResponse: Paginated search results

    Raises:
        HTTPException: If search parameters are invalid
    """
    return await use_case.execute(request)


@router.get(
    "/my",
    response_model=RecipePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Recipes",
    description="Get paginated list of recipes created by the current user",
    response_description="Paginated user recipes",
)
@rate_limit("generous")
async def get_user_recipes(
    use_case: GetUserRecipesUseCaseDep,
    pagination: PaginationParamsDep,
    logged_user: User = Depends(get_current_user),
) -> RecipePageResponse:
    """
    Get recipes created by the authenticated user.

    Retrieves a paginated list of all recipes where the current user is the author.
    Useful for personal recipe management and editing.

    Args:
        pagination: Pagination parameters (page, size, sorting)
        logged_user: Authenticated user (auto-injected)

    Returns:
        RecipePageResponse: Paginated list of user's recipes
    """
    return await use_case.execute(logged_user.id, pagination)


@router.get(
    "/my/favorites",
    response_model=RecipePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Favorite Recipes",
    description="Get paginated list of recipes favorited by the current user",
    response_description="Paginated favorite recipes",
)
@rate_limit("generous")
async def get_user_favorite_recipes(
    use_case: GetUserFavoritesRecipesUseCaseDep,
    pagination: PaginationParamsDep,
    logged_user: User = Depends(get_current_user),
) -> RecipePageResponse:
    """
    Get user's favorite recipes.

    Retrieves a paginated list of recipes that the current user has marked as favorites.
    Presents recipes in a format suitable for browsing and discovery.

    Args:
        pagination: Pagination parameters
        logged_user: Authenticated user

    Returns:
        RecipePageResponse: Paginated list of favorite recipes
    """
    result_page = await use_case.execute(
        logged_user.id, pagination.to_pagination_params()
    )
    return RecipePageResponse.from_page(result_page)


@router.get(
    "/is_favorite/{recipe_id}",
    status_code=status.HTTP_200_OK,
    summary="Check Favorite Status",
    description="Check if a specific recipe is in the user's favorites",
    response_description="Favorite status",
)
@rate_limit("generous")
async def is_favorite_recipe(
    use_case: IsFavoriteUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to check", example=123
    ),
    logged_user: User = Depends(get_current_user),
) -> dict:
    """
    Check if recipe is in user's favorites.

    Quickly determine whether the authenticated user has favorited a specific recipe.
    Useful for UI state management and conditional rendering.

    Args:
        recipe_id: ID of the recipe to check
        logged_user: Authenticated user

    Returns:
        dict: Contains boolean indicating favorite status

    Example Response:
        {"is_favorite": true}
    """
    is_favorite = await use_case.execute(RecipeId(recipe_id), logged_user.id)
    return {"is_favorite": is_favorite}


@router.patch(
    "/{recipe_id}/favorites/toggle",
    status_code=status.HTTP_200_OK,
    summary="Toggle Favorite",
    description="Add or remove a recipe from user's favorites",
    response_description="Toggle operation result",
)
@rate_limit("generous")
async def toggle_favorite(
    use_case: ToggleFavoriteUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to toggle", example=123
    ),
    logged_user: User = Depends(get_current_user),
) -> dict:
    """
    Toggle favorite status for a recipe.

    Adds the recipe to user's favorites if not already favorited,
    or removes it if already in favorites. Provides feedback on the action taken.

    Args:
        recipe_id: ID of the recipe to toggle
        logged_user: Authenticated user

    Returns:
        dict: Message indicating the action performed

    Raises:
        HTTPException: If recipe not found or operation fails
    """
    await use_case.execute(RecipeId(recipe_id), logged_user.id)

    # Note: The use case doesn't return the current state, so we return a generic message
    return {"message": "Favorite status updated successfully"}


@router.post(
    "/",
    response_model=RecipeCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recipe",
    description="Create a new recipe with full details",
    response_description="Created recipe information",
)
@rate_limit("sensitive")
async def create_recipe(
    request: CreateRecipeRequest,
    use_case: CreateRecipeUseCaseDep,
    logged_user: User = Depends(get_current_user),
) -> RecipeCreatedResponse:
    """
    Create a new recipe.

    Creates a comprehensive recipe with all necessary details including:
    - Basic information (name, description, difficulty, cuisine)
    - Ingredients and preparation steps
    - Cooking times and serving information
    - Nutritional information and tags

    Args:
        request: Recipe creation data
        logged_user: Authenticated user who will be set as the author

    Returns:
        RecipeCreatedResponse: Created recipe ID and confirmation

    Raises:
        HTTPException: If validation fails or user not found
    """
    return await use_case.execute(request, logged_user.id)


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recipe Details",
    description="Get complete details for a specific recipe",
    response_description="Complete recipe details",
)
@rate_limit("public")
async def get_recipe(
    use_case: GetRecipeUseCaseDep,
    increment_views: IncrementViewCountUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to retrieve", example=123
    ),
) -> RecipeResponse:
    """
    Get detailed recipe information.

    Retrieves complete recipe details including all metadata, ingredients, steps,
    and analytics. Automatically increments the view counter for analytics.

    Args:
        recipe_id: ID of the recipe to retrieve
        increment_views: Use case for tracking views (auto-injected)
        use_case: Use case for retrieving recipe data

    Returns:
        RecipeResponse: Complete recipe information

    Raises:
        HTTPException: If recipe is not found
    """
    # Increment view count asynchronously (fire and forget)
    await increment_views.execute(RecipeId(recipe_id))

    # Retrieve recipe details
    recipe = await use_case.execute(RecipeId(recipe_id))
    return recipe


@router.put(
    "/{recipe_id}",
    response_model=RecipeUpdatedResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Recipe",
    description="Update an existing recipe with new information",
    response_description="Updated recipe information",
)
@rate_limit("sensitive")
async def update_recipe(
    request: UpdateRecipeRequest,
    use_case: UpdateRecipeUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to update", example=123
    ),
    logged_user: User = Depends(get_current_user),
) -> RecipeUpdatedResponse:
    """
    Update an existing recipe.

    Allows partial or complete updates to recipe information. Only the recipe author
    or users with appropriate permissions can update recipes.

    Args:
        recipe_id: ID of the recipe to update
        request: Updated recipe data (partial updates supported)
        logged_user: Authenticated user (must be recipe author)

    Returns:
        RecipeUpdatedResponse: Updated recipe information with new version

    Raises:
        HTTPException: If recipe not found or user not authorized
    """
    try:
        result = await use_case.execute(RecipeId(recipe_id), request, logged_user.id)
        return result

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RecipeValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "code": e.error_code},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recipe update failed",
        )


@router.get(
    "/{recipe_id}/reviews",
    response_model=ReviewPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recipe Reviews",
    description="Retrieve paginated reviews for a specific recipe",
    response_description="Paginated recipe reviews",
)
@rate_limit("public")
async def get_recipe_reviews(
    use_case: GetRecipeReviewsUseCaseDep,
    pagination: PaginationParamsDep,
    recipe_id: int = Path(..., gt=0, description="The ID of the recipe", example=123),
) -> ReviewPageResponse:
    """
    Get paginated reviews for a recipe.

    Retrieves user-submitted reviews for the specified recipe, including ratings
    and comments. Supports pagination for efficient browsing.

    Args:
        recipe_id: ID of the recipe
        pagination: Pagination parameters (page, size, sorting)
    Returns:
        ReviewPageResponse: Paginated list of reviews for the recipe
    return await use_case.execute(RecipeId(recipe_id), pagination)
    """
    return await use_case.execute(
        RecipeId(recipe_id), pagination.to_pagination_params()
    )


@router.get(
    "/{recipe_id}/reviews/my",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User's Review for Recipe",
    description="Retrieve the authenticated user's review for a specific recipe",
    response_description="User's review for the recipe",
)
@rate_limit("generous")
async def get_user_review_for_recipe(
    use_case: GetUserReviewForRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="The ID of the recipe", example=123),
    logged_user: User = Depends(get_current_user),
) -> ReviewResponse:
    """
    Get the authenticated user's review for a specific recipe.

    Retrieves the review submitted by the current user for the specified recipe,
    if it exists. Useful for displaying or editing the user's own review.

    Args:
        recipe_id: ID of the recipe
        logged_user: Authenticated user
    Returns:
        ReviewResponse: The user's review for the recipe
    """
    return await use_case.execute(RecipeId(recipe_id), logged_user.id)


@router.post(
    "/{recipe_id}/reviews",
    response_model=ReviewCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Review",
    description="Add a review and rating to a recipe",
    response_description="Review creation result with updated reviews",
)
@rate_limit("sensitive")
async def add_review(
    request: CreateReviewRequest,
    use_case: CreateReviewUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="The ID of the recipe", example=123),
    logged_user: User = Depends(get_current_user),
) -> ReviewCreatedResponse:
    """
    Add a review to a recipe.

    Users can submit reviews with reviews (1-5 stars) and optional comments.
    Each user can only review a recipe once. Reviews impact the recipe's average rating.

    Args:
        request: Review data including rating and optional comment
        logged_user: Authenticated user submitting the review

    Returns:
        ReviewCreatedResponse: Review confirmation with updated average rating

    Raises:
        HTTPException: If validation fails or duplicate review detected
    """
    return await use_case.execute(request, logged_user.id, RecipeId(recipe_id))


@router.patch(
    "/{recipe_id}/reviews",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update Review",
    description="Update a user's review for a recipe",
    response_description="Review update result with updated reviews",
)
@rate_limit("sensitive")
async def update_review(
    request: UpdateReviewRequest,
    use_case: UpdateReviewUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="The ID of the recipe", example=123),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Update a user's review for a recipe.

    Allows users to modify their existing reviews. This will update the recipe's
    average rating and review count accordingly.

    Args:
        request: Updated review data including new rating and optional comment
        recipe_id: ID of the recipe
        logged_user: Authenticated user (must be the review author)
    """
    await use_case.execute(logged_user.id, RecipeId(recipe_id), request)


@router.delete(
    "/{recipe_id}/reviews",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Review",
    description="Remove a user's review from a recipe",
)
@rate_limit("sensitive")
async def delete_review(
    use_case: DeleteReviewUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="The ID of the recipe", example=123),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a user's review from a recipe.

    Allows users to remove their own reviews. This will update the recipe's
    average rating and review count accordingly.

    Args:
        recipe_id: ID of the recipe
        logged_user: Authenticated user (must be the review author)

    Raises:
        HTTPException: If recipe not found or review doesn't exist
    """
    await use_case.execute(RecipeId(recipe_id), logged_user.id)


@router.post(
    "/{recipe_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Restore Recipe",
    description="Restore a soft-deleted recipe (admin/author only)",
)
@rate_limit("sensitive")
async def restore_recipe(
    use_case: RestoreRecipeUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to restore", example=123
    ),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Restore a soft-deleted recipe.

    Allows recipe authors or administrators to restore recipes that were
    previously soft-deleted. The recipe will become visible in searches again.

    Args:
        recipe_id: ID of the recipe to restore
        logged_user: Authenticated user (must be author or admin)

    Raises:
        HTTPException: If recipe not found or user not authorized
    """
    await use_case.execute(RecipeId(recipe_id))


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Recipe",
    description="Soft delete a recipe (author only)",
)
@rate_limit("sensitive")
async def delete_recipe(
    use_case: DeleteRecipeUseCaseDep,
    recipe_id: int = Path(
        ..., gt=0, description="The ID of the recipe to delete", example=123
    ),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Soft delete a recipe.

    Marks a recipe as deleted without permanently removing it from the database.
    Only the recipe author or users with appropriate permissions can delete recipes.
    Deleted recipes are not visible in normal searches but can be restored.

    Args:
        recipe_id: ID of the recipe to delete
        logged_user: Authenticated user (must be recipe author)

    Raises:
        HTTPException: If recipe not found or user not authorized
    """
    await use_case.execute(RecipeId(recipe_id), logged_user.id)
