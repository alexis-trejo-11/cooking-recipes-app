from fastapi import Query
from fastapi import Depends
from typing import Optional
from app.config.sql_session import get_db_session
from app.config.app_settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated
from app.modules.recipe.infrastructure.persistence.repository import (
    SQLAlchemyRecipeRepository,
)
from app.modules.recipe.domain.interfaces import RecipeRepository
from app.modules.recipe.application.use_cases.base import (
    CreateRecipeUseCase,
    GetRecipeUseCase,
    RestoreRecipeUseCase,
    SearchRecipesUseCase,
    AddRatingUseCase,
    IncrementViewCountUseCase,
    GetUserRecipesUseCase,
    IncreaseFavoriteUseCase,
    DecreaseFavoriteUseCase,
    UpdateRecipeUseCase,
    DeleteRecipeUseCase,
)

from app.modules.recipe.application.use_cases.command_recipe_use_case import (
    CreateRecipeUseCaseImpl,
    AddRatingUseCaseImpl,
    IncrementViewCountUseCaseImpl,
    UpdateRecipeUseCaseImpl,
    DeleteRecipeUseCaseImpl,
    IncreaseFavoriteUseCaseImpl,
    DecreaseFavoriteUseCaseImpl,
    RestoreRecipeUseCaseImpl,
)
from app.modules.recipe.application.use_cases.query_recipe_use_case import (
    GetRecipeUseCaseImpl,
    SearchRecipesUseCaseImpl,
    GetUserRecipesUseCaseImpl,
)
from app.modules.recipe.application.dtos import RecipeSearchRequest


from app.modules.auth.presentation.app_depencies import UserRepositoryDep
from app.utils.external.page_request import PydanticPaginationParams as PaginationParams


async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for database session.
    Ensures proper cleanup after request.
    """
    async for session in get_db_session():
        try:
            yield session
        finally:
            await session.close()


async def get_recipe_repository(
    session: Annotated[AsyncSession, Depends(get_db_session_dependency)],
) -> RecipeRepository:
    """
    Dependency for RecipeRepository.
    Provides SQLAlchemy implementation.
    """
    return SQLAlchemyRecipeRepository(session)


async def get_add_rating_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> AddRatingUseCase:
    """
    Dependency for AddRatingUseCase.
    """
    return AddRatingUseCaseImpl(recipe_repository)


async def get_increment_view_count_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> IncrementViewCountUseCase:
    """
    Dependency for IncrementViewCountUseCase.
    """
    return IncrementViewCountUseCaseImpl(recipe_repository)


async def get_create_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    user_repository: UserRepositoryDep,
) -> CreateRecipeUseCase:
    """
    Dependency for CreateRecipeUseCase.
    """
    return CreateRecipeUseCaseImpl(recipe_repository, user_repository)


async def get_update_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> UpdateRecipeUseCase:
    """
    Dependency for UpdateRecipeUseCase.
    """
    return UpdateRecipeUseCaseImpl(recipe_repository)


async def get_increase_favorite_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> IncreaseFavoriteUseCase:
    """
    Dependency for IncreaseFavoriteUseCase.
    """
    return IncreaseFavoriteUseCaseImpl(recipe_repository)


async def get_decrease_favorite_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> DecreaseFavoriteUseCase:
    """
    Dependency for DecreaseFavoriteUseCase.
    """
    return DecreaseFavoriteUseCaseImpl(recipe_repository)


async def get_delete_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> DeleteRecipeUseCase:
    """
    Dependency for DeleteRecipeUseCase.
    """
    return DeleteRecipeUseCaseImpl(recipe_repository)


async def get_get_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetRecipeUseCase:
    """
    Dependency for GetRecipeUseCase.
    """
    return GetRecipeUseCaseImpl(recipe_repository)


async def get_search_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> SearchRecipesUseCase:
    """
    Dependency for SearchRecipesUseCase.
    """
    return SearchRecipesUseCaseImpl(recipe_repository)


async def get_get_user_recipes_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> GetUserRecipesUseCase:
    """
    Dependency for GetUserRecipesUseCase.
    """
    return GetUserRecipesUseCaseImpl(recipe_repository)


async def get_restore_recipe_use_case(
    recipe_repository: Annotated[RecipeRepository, Depends(get_recipe_repository)],
) -> RestoreRecipeUseCase:
    """
    Dependency for RestoreRecipeUseCase.
    """
    return RestoreRecipeUseCaseImpl(recipe_repository)


def get_pagination_params(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_dir: str = Query("asc", regex="^(asc|desc)$"),
    sort_by: str = Query("created_at"),
) -> PaginationParams:
    """
    Dependency for pagination parameters.
    """
    return PaginationParams(page=page, size=size, sort_dir=sort_dir, sort_by=sort_by)


def get_recipe_search_request(
    pagination: PaginationParams = Depends(get_pagination_params),
    name: Optional[str] = Query(None, min_length=1, max_length=200),
    author_id: Optional[int] = Query(None, ge=1),
    difficulty: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    meal_types: Optional[set[str]] = Query(None),
    tags: Optional[set[str]] = Query(None),
    ingredient_name: Optional[str] = Query(None),
    max_cook_time: Optional[int] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0),
) -> RecipeSearchRequest:
    """
    Dependency for RecipeSearchRequest.
    """
    return RecipeSearchRequest(
        name=name,
        author_id=author_id,
        difficulty=difficulty,
        cuisine=cuisine,
        meal_types=list(meal_types) if meal_types else None,
        ingredient_name=ingredient_name,
        max_cooking_time=max_cook_time,
        include_deleted=False,
        tags=list(tags) if tags else None,
        min_rating=min_rating,
        pagination=pagination,
    )


# Command Use Case Dependencies
AddRatingUseCaseDep = Annotated[AddRatingUseCase, Depends(get_add_rating_use_case)]


CreateRecipeUseCaseDep = Annotated[
    CreateRecipeUseCase,
    Depends(get_create_recipe_use_case),
]

IncrementViewCountUseCaseDep = Annotated[
    IncrementViewCountUseCase,
    Depends(get_increment_view_count_use_case),
]

UpdateRecipeUseCaseDep = Annotated[
    UpdateRecipeUseCase,
    Depends(get_update_recipe_use_case),
]

DeleteRecipeUseCaseDep = Annotated[
    DeleteRecipeUseCase,
    Depends(get_delete_recipe_use_case),
]

IncreaseFavoriteUseCaseDep = Annotated[
    IncreaseFavoriteUseCase, Depends(get_increase_favorite_use_case)
]

DecreaseFavoriteUseCaseDep = Annotated[
    DecreaseFavoriteUseCase, Depends(get_decrease_favorite_use_case)
]

RestoreRecipeUseCaseDep = Annotated[
    RestoreRecipeUseCase, Depends(get_restore_recipe_use_case)
]

# Query Use Case Dependencies
GetUserRecipesUseCaseDep = Annotated[
    GetUserRecipesUseCase, Depends(get_get_user_recipes_use_case)
]

GetRecipeUseCaseDep = Annotated[GetRecipeUseCase, Depends(get_get_recipe_use_case)]

SearchRecipesUseCaseDep = Annotated[
    SearchRecipesUseCase, Depends(get_search_recipes_use_case)
]
