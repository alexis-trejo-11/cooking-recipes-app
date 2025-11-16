from fastapi import APIRouter, status, Path
from app.modules.auth.presentation.auth_depencies import get_current_user
from app.modules.auth.domain.user import User
from app.modules.recipe.application.dtos import *
from app.modules.recipe.application.exceptions import *
from .dependencies import *
from app.config.rate_limiter import rate_limit

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])


@rate_limit("public")
@router.get(
    "/featured",
    response_model=List[RecipeSummaryResponse],
    summary="Get Featured Recipes",
)
async def get_featured_recipes(
    use_case: GetFeaturedRecipesUseCaseDep,
) -> List[RecipeSummaryResponse]:
    """
    Get a list of featured recipes.
    """
    return await use_case.execute()


@rate_limit("public")
@router.get(
    "",
    response_model=RecipePageResponse,
    summary="Search Recipes",
    description="Search recipes with filters",
)
async def search_recipes(
    use_case: SearchRecipesUseCaseDep,
    request: RecipeSearchRequest = Depends(get_recipe_search_request),
) -> RecipePageResponse:
    """
    Search recipes with advanced filters.

    - **query**: Search query text
    - **difficulty**: Filter by difficulty level
    - **cuisine**: Filter by cuisine type
    - **meal_type**: Filter by meal type
    - **diet**: Filter by diet type
    - **max_prep_time**: Maximum preparation time
    - **max_cook_time**: Maximum cooking time
    - **min_rating**: Minimum average rating
    - **tags**: Filter by tags
    - **exclude_allergens**: Exclude recipes with these allergens
    - **page**: Page number
    - **page_size**: Page size
    """
    return await use_case.execute(request)


@rate_limit("generous")
@router.get(
    "/user/",
    response_model=RecipePageResponse,
    summary="Get User Recipes",
    description="Get paginated list of recipes by user",
)
async def get_user_recipes(
    use_case: GetUserRecipesUseCaseDep,
    pagination: PaginationParams = Depends(get_pagination_params),
    logged_user: User = Depends(get_current_user),
) -> RecipePageResponse:
    """
    Get paginated list of recipes created by the current user.
    - **page**: Page number
    - **page_size**: Page size
    """
    return await use_case.execute(logged_user.id, pagination)


@router.post(
    "/",
    response_model=RecipeCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recipe",
    description="Create a new recipe",
)
@rate_limit("sensitive")
async def create_recipe(
    request: CreateRecipeRequest,
    use_case: CreateRecipeUseCaseDep,
    logged_user: User = Depends(get_current_user),
) -> RecipeCreatedResponse:
    """
    Create a new recipe.

    - **name**: Recipe name (1-200 characters)
    - **description**: Optional recipe description
    - **difficulty**: Recipe difficulty level
    - **cuisine**: Optional cuisine type
    - **ingredients**: List of ingredients
    - **steps**: List of preparation steps
    - **tags**: List of tags
    - **meal_types**: List of meal types
    - **servings**: Number of servings
    - **prep_time_minutes**: Preparation time in minutes
    - **cook_time_minutes**: Cooking time in minutes
    - **nutritional_info**: Optional nutritional information
    """
    result = await use_case.execute(request, logged_user.id)
    return result


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get Recipe",
    description="Get recipe details by ID",
)
@rate_limit("public")
async def get_recipe(
    use_case: GetRecipeUseCaseDep,
    increment_views: IncrementViewCountUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
) -> RecipeResponse:
    """
    Get detailed recipe information by ID.

    - **recipe_id**: Recipe identifier
    """
    await increment_views.execute(RecipeId(recipe_id))

    recipe = await use_case.execute(RecipeId(recipe_id))
    return recipe


@router.put(
    "/{recipe_id}",
    response_model=RecipeUpdatedResponse,
    summary="Update Recipe",
    description="Update an existing recipe",
)
@rate_limit("sensitive")
async def update_recipe(
    request: UpdateRecipeRequest,
    use_case: UpdateRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    logged_user: User = Depends(get_current_user),
) -> RecipeUpdatedResponse:
    """
    Update an existing recipe.

    - **recipe_id**: Recipe identifier
    - **name**: Optional updated recipe name
    - **description**: Optional updated description
    - **difficulty**: Optional updated difficulty
    - **ingredients**: Optional updated ingredients list
    - **steps**: Optional updated steps list
    - **tags**: Optional updated tags
    """
    result = await use_case.execute(RecipeId(recipe_id), request, logged_user.id)
    return result


@router.post(
    "/{recipe_id}/ratings",
    response_model=ReviewCreatedResponse,
    summary="Add Rating",
    description="Add a rating to a recipe",
)
@rate_limit("sensitive")
async def add_review(
    request: CreateReviewRequest,
    use_case: CreateReviewUseCaseDep,
    logged_user: User = Depends(get_current_user),
) -> ReviewCreatedResponse:
    """
    Add a review to a recipe.

    - **recipe_id**: Recipe identifier
    - **rating**: Rating value (1-5)
    """
    return await use_case.execute(request)


@router.delete(
    "/{recipe_id}/ratings",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Rating",
    description="Delete a rating from a recipe",
)
@rate_limit("sensitive")
async def delete_review(
    use_case: DeleteReviewUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a review from a recipe.

    - **recipe_id**: Recipe identifier
    """
    await use_case.execute(RecipeId(recipe_id), logged_user.id)


@router.patch(
    "/{recipe_id}/favorites/toggle",
    summary="Toggle Favorite",
    description="Add or remove recipe from favorites",
)
@rate_limit("generous")
async def toggle_favorite(
    use_case: ToggleFavoriteUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    logged_user: User = Depends(get_current_user),
):
    """
    Add recipe to user's favorites.

    - **recipe_id**: Recipe identifier
    """
    added = await use_case.execute(RecipeId(recipe_id), logged_user.id)
    if added:
        return {"message": "Recipe added to favorites"}

    return {"message": "Recipe removed from favorites"}


@router.post(
    "/{recipe_id}/restore",
    summary="Restore Recipe",
    description="Restore a soft-deleted recipe",
    status_code=status.HTTP_204_NO_CONTENT,
)
@rate_limit("sensitive")
async def restore_recipe(
    use_case: RestoreRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    logged_user: User = Depends(get_current_user),
):
    """
    Restore a soft-deleted recipe.

    - **recipe_id**: Recipe identifier
    """
    await use_case.execute(RecipeId(recipe_id))


@router.delete(
    "/{recipe_id}",
    summary="Delete Recipe",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a recipe (soft delete)",
)
@rate_limit("sensitive")
async def delete_recipe(
    use_case: DeleteRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    logged_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a recipe (soft delete).

    - **recipe_id**: Recipe identifier
    """
    await use_case.execute(RecipeId(recipe_id), logged_user.id)
