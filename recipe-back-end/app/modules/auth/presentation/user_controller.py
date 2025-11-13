from fastapi import APIRouter, Depends, status
from .app_depencies import (
    GetUserProfileUseCaseDep,
    UpdateUserProfileUseCaseDep,
)
from .auth_depencies import get_current_user
from app.modules.auth.domain.user import User
from app.modules.auth.application.dtos import (
    UserProfileResponse,
    UpdateUserProfileRequest,
)
from app.modules.recipe.application.dtos import RecipePageResponse
from app.modules.recipe.presentation.dependencies import (
    GetRecipeFavoritesByUserUseCaseDep,
    get_pagination_params,
)
from app.utils.external.page_request import PydanticPaginationParams


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get(
    "/me", summary="Get Current User Profile", response_model=UserProfileResponse
)
async def get_current_user_profile(
    use_case: GetUserProfileUseCaseDep,
    current_user: User = Depends(get_current_user),
):
    return await use_case.execute(current_user)


@router.put(
    "/me",
    summary="Update Current User Profile",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_current_user_profile(
    use_case: UpdateUserProfileUseCaseDep,
    request: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Update the profile of the currently authenticated user.

    - **first_name**: User's first name (2-50 characters)
    - **last_name**: User's last name (2-50 characters)
    - **phone_number**: Optional phone number in international format
    """
    await use_case.execute(current_user.id, request)


@router.get(
    "/recipes/favs",
    summary="Get User's Favorite Recipes",
    response_model=RecipePageResponse,
)
async def get_user_favorite_recipes(
    use_case: GetRecipeFavoritesByUserUseCaseDep,
    current_user: User = Depends(get_current_user),
    pagination: PydanticPaginationParams = Depends(get_pagination_params),
) -> RecipePageResponse:
    """
    Retrieve a list of the user's favorite recipes.
    """
    recipe_page = await use_case.execute(
        current_user.id, pagination.to_pagination_params()
    )
    return RecipePageResponse.from_page(recipe_page)
