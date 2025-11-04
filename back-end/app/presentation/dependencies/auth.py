from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated

from app.application.usecases.auth_use_cases import SignUpUseCase, LoginUseCase
from app.application.interfaces.password_hasher import PasswordHasher
from app.application.interfaces.token_service import TokenService
from app.application.interfaces.user_repository import UserRepository

from app.infrastructure.services.jwt_token_service import JWTTokenService
from app.infrastructure.services.bcrypt_password_hasher import BCryptPasswordHasher
from app.infrastructure.persistence.repository.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

from config.sql_session import get_db_session
from config.config import settings


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


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session_dependency)],
) -> UserRepository:
    """
    Dependency for UserRepository.
    Provides SQLAlchemy implementation.
    """
    return SQLAlchemyUserRepository(session)


async def get_password_hasher() -> PasswordHasher:
    """
    Dependency for PasswordHasher.
    Provides bcrypt implementation.
    """
    return BCryptPasswordHasher()


async def get_token_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenService:
    """
    Dependency for TokenService.
    Provides JWT implementation with configuration from settings.
    """
    return JWTTokenService(
        user_repository=user_repository,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRES,
    )


def get_signup_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> SignUpUseCase:
    """
    Dependency for SignUpUseCase.
    Injects all required dependencies.
    """
    return SignUpUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_login_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LoginUseCase:
    """
    Dependency for LoginUseCase.
    Injects all required dependencies.
    """
    return LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
    )


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
SignUpUseCaseDep = Annotated[SignUpUseCase, Depends(get_signup_use_case)]
LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
