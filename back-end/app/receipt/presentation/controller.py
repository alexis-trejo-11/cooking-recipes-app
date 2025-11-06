# recipe_controller.py
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import Optional, List
from app.receipt.application.dtos import *
from app.receipt.application.use_cases.base import *
from .dependencies import *
from app.receipt.application.exceptions import *

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
    # En producción, obtendrías el user_id del token JWT
    # current_user: User = Depends(get_current_user)
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
    try:
        # TODO: Obtener user_id real del token JWT
        author_id = 1  # Temporal - reemplazar con current_user.id
        result = await use_case.execute(request, author_id)
        return result

    except RecipeValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the recipe",
        )


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get Recipe",
    description="Get recipe details by ID",
)
async def get_recipe(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: GetRecipeUseCaseDep = Depends(),
    increment_views: IncrementViewCountUseCaseDep = Depends(),
) -> RecipeResponse:
    """
    Get detailed recipe information by ID.

    - **recipe_id**: Recipe identifier
    """
    try:
        # Increment view count
        await increment_views.execute(recipe_id)

        recipe = await use_case.execute(recipe_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found",
            )
        return recipe

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the recipe",
        )


@router.put(
    "/{recipe_id}",
    response_model=RecipeUpdatedResponse,
    summary="Update Recipe",
    description="Update an existing recipe",
)
async def update_recipe(
    request: UpdateRecipeRequest,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: UpdateRecipeUseCaseDep = Depends(),
    # current_user: User = Depends(get_current_user)
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
    try:
        # TODO: Obtener user_id real del token JWT
        user_id = 1  # Temporal - reemplazar con current_user.id
        result = await use_case.execute(recipe_id, request, user_id)
        return result

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RecipeValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except UnauthorizedAccessException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the recipe",
        )


@router.delete(
    "/{recipe_id}",
    response_model=RecipeDeletedResponse,
    summary="Delete Recipe",
    description="Delete a recipe (soft delete)",
)
async def delete_recipe(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: DeleteRecipeUseCaseDep = Depends(),
    # current_user: User = Depends(get_current_user)
) -> RecipeDeletedResponse:
    """
    Delete a recipe (soft delete).

    - **recipe_id**: Recipe identifier
    """
    try:
        # TODO: Obtener user_id real del token JWT
        user_id = 1  # Temporal - reemplazar con current_user.id
        result = await use_case.execute(recipe_id, user_id)
        return result

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedAccessException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the recipe",
        )


@router.get(
    "/",
    response_model=PaginatedRecipesResponse,
    summary="List Recipes",
    description="Get paginated list of recipes",
)
async def list_recipes(
    page: int = Query(1, gt=0, description="Page number"),
    page_size: int = Query(20, gt=0, le=100, description="Page size"),
    use_case: ListRecipesUseCaseDep = Depends(),
) -> PaginatedRecipesResponse:
    """
    Get paginated list of recipes.

    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 20, max: 100)
    """
    try:
        return await use_case.execute(page, page_size)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing recipes",
        )


@router.post(
    "/search",
    response_model=PaginatedRecipesResponse,
    summary="Search Recipes",
    description="Search recipes with filters",
)
async def search_recipes(
    request: RecipeSearchRequest, use_case: SearchRecipesUseCaseDep = Depends()
) -> PaginatedRecipesResponse:
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
    try:
        return await use_case.execute(request)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching recipes",
        )


@router.post(
    "/by-ingredients",
    response_model=PaginatedRecipesResponse,
    summary="Find Recipes by Ingredients",
    description="Find recipes that contain specific ingredients",
)
async def find_recipes_by_ingredients(
    request: FindByIngredientsRequest,
    use_case: FindRecipesByIngredientsUseCaseDep = Depends(),
) -> PaginatedRecipesResponse:
    """
    Find recipes that contain specific ingredients.

    - **ingredients**: List of ingredient names to search for
    - **include_optional**: Whether to include optional ingredients in search
    - **page**: Page number
    - **page_size**: Page size
    """
    try:
        return await use_case.execute(request)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching recipes by ingredients",
        )


@router.post(
    "/{recipe_id}/scale",
    response_model=RecipeScaledResponse,
    summary="Scale Recipe",
    description="Create a scaled version of a recipe",
)
async def scale_recipe(
    request: ScaleRecipeRequest,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: ScaleRecipeUseCaseDep = Depends(),
    # current_user: User = Depends(get_current_user)
) -> RecipeScaledResponse:
    """
    Create a scaled version of a recipe.

    - **recipe_id**: Original recipe ID
    - **factor**: Scaling factor (e.g., 2.0 to double the recipe)
    - **adjust_cooking_time**: Whether to adjust cooking time
    """
    try:
        # TODO: Obtener user_id real del token JWT
        user_id = 1  # Temporal - reemplazar con current_user.id
        return await use_case.execute(recipe_id, request, user_id)

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RecipeValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while scaling the recipe",
        )


@router.post(
    "/{recipe_id}/ratings",
    response_model=RatingAddedResponse,
    summary="Add Rating",
    description="Add a rating to a recipe",
)
async def add_rating(
    request: AddRatingRequest,
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: AddRatingUseCaseDep = Depends(),
    # current_user: User = Depends(get_current_user)
) -> RatingAddedResponse:
    """
    Add a rating to a recipe.

    - **recipe_id**: Recipe identifier
    - **rating**: Rating value (1-5)
    """
    try:
        # TODO: Obtener user_id real del token JWT
        user_id = 1  # Temporal - reemplazar con current_user.id
        return await use_case.execute(recipe_id, request, user_id)

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RecipeValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the rating",
        )


@router.post(
    "/{recipe_id}/favorites",
    summary="Toggle Favorite",
    description="Add or remove recipe from favorites",
)
async def toggle_favorite(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: ToggleFavoriteUseCaseDep = Depends(),
    # current_user: User = Depends(get_current_user)
):
    """
    Add or remove recipe from user's favorites.

    - **recipe_id**: Recipe identifier
    """
    try:
        # TODO: Obtener user_id real del token JWT
        user_id = 1  # Temporal - reemplazar con current_user.id
        added = await use_case.execute(recipe_id, user_id)

        if added:
            return {"message": "Recipe added to favorites"}
        else:
            return {"message": "Recipe removed from favorites"}

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while toggling favorite",
        )


@router.get(
    "/user/{user_id}",
    response_model=PaginatedRecipesResponse,
    summary="Get User Recipes",
    description="Get paginated list of recipes by user",
)
async def get_user_recipes(
    user_id: int = Path(..., gt=0, description="User ID"),
    page: int = Query(1, gt=0, description="Page number"),
    page_size: int = Query(20, gt=0, le=100, description="Page size"),
    use_case: GetUserRecipesUseCaseDep = Depends(),
) -> PaginatedRecipesResponse:
    """
    Get paginated list of recipes created by a specific user.

    - **user_id**: User identifier
    - **page**: Page number
    - **page_size**: Page size
    """
    try:
        return await use_case.execute(user_id, page, page_size)

    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving user recipes",
        )


@router.get(
    "/{recipe_id}/compatible-diets",
    response_model=List[DietType],
    summary="Get Compatible Diets",
    description="Get list of diets compatible with the recipe",
)
async def get_compatible_diets(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: GetRecipeCompatibleDietsUseCaseDep = Depends(),
) -> List[DietType]:
    """
    Get list of diets that are compatible with the recipe.

    - **recipe_id**: Recipe identifier
    """
    try:
        return await use_case.execute(recipe_id)

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving compatible diets",
        )


@router.get(
    "/{recipe_id}/allergens",
    response_model=List[str],
    summary="Get Allergens",
    description="Get list of allergens present in the recipe",
)
async def get_allergens(
    recipe_id: int = Path(..., gt=0, description="Recipe ID"),
    use_case: GetRecipeAllergensUseCaseDep = Depends(),
) -> List[str]:
    """
    Get list of allergens present in the recipe ingredients.

    - **recipe_id**: Recipe identifier
    """
    try:
        return await use_case.execute(recipe_id)

    except RecipeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving allergens",
        )
