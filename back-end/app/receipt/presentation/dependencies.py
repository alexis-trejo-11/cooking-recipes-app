from fastapi import Depends
from config.sql_session import get_db_session
from config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated
from app.receipt.infrastructure.persistence.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)
from app.receipt.domain.interfaces import RecipeRepository
from app.receipt.application.usecases.use_cases import (
    CreateRecipeUseCase,
    GetRecipeUseCase,
    ListRecipesUseCase,
    UpdateRecipeUseCase,
    DeleteRecipeUseCase,
)


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


CreateRecipeUseCaseDep = Annotated[
    CreateRecipeUseCase,
    Depends(),
]
GetRecipeUseCaseDep = Annotated[GetRecipeUseCase, Depends()]
ListRecipesUseCaseDep = Annotated[ListRecipesUseCase, Depends()]
UpdateRecipeUseCaseDep = Annotated[
    UpdateRecipeUseCase,
    Depends(),
]
DeleteRecipeUseCaseDep = Annotated[
    DeleteRecipeUseCase,
    Depends(),
]
