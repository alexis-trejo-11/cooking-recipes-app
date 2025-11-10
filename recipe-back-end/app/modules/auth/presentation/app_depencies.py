from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated
from app.modules.auth.application.auth_use_cases import SignUpUseCase, LoginUseCase
from app.modules.auth.domain.interfaces import (
    UserRepository,
    TokenService,
    PasswordHasher,
)
from app.modules.auth.infrastucture.services.jwt_token_service import JWTTokenService
from app.modules.auth.infrastucture.services.bcrypt_password_hasher import (
    BCryptPasswordHasher,
)
from app.modules.auth.infrastucture.persitence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.config.sql_session import get_db_session
from app.config.app_settings import settings

security = HTTPBearer(auto_error=False)


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


# Application dependencies
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
SignUpUseCaseDep = Annotated[SignUpUseCase, Depends(get_signup_use_case)]
LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
