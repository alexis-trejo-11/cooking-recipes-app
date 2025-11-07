from fastapi import APIRouter, HTTPException, status, Query, Path
from app.modules.auth.presentation.auth_depencies import get_current_user
from app.modules.auth.domain.user import User
from app.modules.recipe.application.dtos import *
from app.modules.recipe.application.use_cases.base import *
from app.modules.recipe.application.exceptions import *
from .dependencies import *
from app.utils.external.page_request import PydanticPaginationParams as PaginationParams

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])


@router.post(
    "/",
    response_model=RecipeCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recipe",
    description="Create a new recipe",
)
async def create_recipe(
    request: CreateRecipeRequest,
    use_case: CreateRecipeUseCaseDep,
    current_user: User = Depends(get_current_user),
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
    result = await use_case.execute(request, current_user.user_id)
    return result


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get Recipe",
    description="Get recipe details by ID",
)
async def get_recipe(
    use_case: GetRecipeUseCaseDep,
    increment_views: IncrementViewCountUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
) -> RecipeResponse:
    """
    Get detailed recipe information by ID.

    - **recipe_id**: Recipe identifier
    """
    await increment_views.execute(recipe_id)

    recipe = await use_case.execute(recipe_id)
    return recipe


@router.put(
    "/{recipe_id}",
    response_model=RecipeUpdatedResponse,
    summary="Update Recipe",
    description="Update an existing recipe",
)
async def update_recipe(
    request: UpdateRecipeRequest,
    use_case: UpdateRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    current_user: User = Depends(get_current_user),
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
    result = await use_case.execute(RecipeId(recipe_id), request, current_user.user_id)
    return result


@router.delete(
    "/{recipe_id}",
    response_model=RecipeDeletedResponse,
    summary="Delete Recipe",
    description="Delete a recipe (soft delete)",
)
async def delete_recipe(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: DeleteRecipeUseCaseDep = Depends(),
    current_user: User = Depends(get_current_user),
) -> RecipeDeletedResponse:
    """
    Delete a recipe (soft delete).

    - **recipe_id**: Recipe identifier
    """
    result = await use_case.execute(RecipeId(recipe_id), current_user.user_id)
    return result


@router.post(
    "/search",
    response_model=RecipePageResponse,
    summary="Search Recipes",
    description="Search recipes with filters",
)
async def search_recipes(
    request: RecipeSearchRequest, use_case: SearchRecipesUseCaseDep
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


@router.post(
    "/{recipe_id}/ratings",
    response_model=RatingAddedResponse,
    summary="Add Rating",
    description="Add a rating to a recipe",
)
async def add_rating(
    request: AddRatingRequest,
    use_case: AddRatingUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    current_user: User = Depends(get_current_user),
) -> RatingAddedResponse:
    """
    Add a rating to a recipe.

    - **recipe_id**: Recipe identifier
    - **rating**: Rating value (1-5)
    """
    return await use_case.execute(RecipeId(recipe_id), request, current_user.user_id)


@router.patch(
    "/{recipe_id}/favorites/increase",
    summary="Increase Favorite",
    description="Add recipe to favorites",
)
async def increase_favorite(
    use_case: IncreaseFavoriteUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    current_user: User = Depends(get_current_user),
):
    """
    Add recipe to user's favorites.

    - **recipe_id**: Recipe identifier
    """
    added = await use_case.execute(RecipeId(recipe_id), current_user.user_id)
    if added:
        return {"message": "Recipe added to favorites"}

    return {"message": "Recipe removed from favorites"}


@router.patch(
    "/{recipe_id}/favorites/decrease",
    summary="Decrease Favorite",
    description="Remove recipe from favorites",
)
async def decrease_favorite(
    use_case: DecreaseFavoriteUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    current_user: User = Depends(get_current_user),
):
    """
    Remove recipe from user's favorites.

    - **recipe_id**: Recipe identifier
    """
    removed = await use_case.execute(RecipeId(recipe_id), current_user.user_id)
    if removed:
        return {"message": "Recipe removed from favorites"}

    return {"message": "Recipe was not in favorites"}


@router.post(
    "/{recipe_id}/restore",
    summary="Restore Recipe",
    description="Restore a soft-deleted recipe",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def restore_recipe(
    use_case: RestoreRecipeUseCaseDep,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    current_user: User = Depends(get_current_user),
):
    """
    Restore a soft-deleted recipe.

    - **recipe_id**: Recipe identifier
    """
    await use_case.execute(RecipeId(recipe_id), current_user.user_id)


@router.get(
    "/user/{user_id}",
    response_model=RecipePageResponse,
    summary="Get User Recipes",
    description="Get paginated list of recipes by user",
)
async def get_user_recipes(
    use_case: GetUserRecipesUseCaseDep,
    pagination: PaginationParams,
    current_user: User = Depends(get_current_user),
) -> RecipePageResponse:
    """
    Get paginated list of recipes created by a specific user.

    - **user_id**: User identifier
    - **page**: Page number
    - **page_size**: Page size
    """
    return await use_case.execute(current_user.user_id, pagination)
