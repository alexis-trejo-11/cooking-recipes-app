from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated, Optional
from app.modules.auth.application.auth_use_cases import (
    SignUpUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
)
from app.modules.auth.application.user_use_cases import (
    UpdateUserProfileUseCase,
    GetUserProfileUseCase,
)
from app.modules.auth.domain.interfaces import (
    UserRepository,
    EnhancedTokenService as TokenService,
    PasswordHasher,
    SessionRepository,
)
from app.modules.auth.infrastucture.services.jwt_token_service import JWTTokenService
from app.modules.auth.infrastucture.services.bcrypt_password_hasher import (
    BCryptPasswordHasher,
)
from app.modules.auth.infrastucture.persitence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.modules.auth.infrastucture.persitence.redis_user_session_repository import (
    RedisSessionRepository,
)
from app.config.sql_session import get_db_session
from app.config.app_settings import settings
from app.config.redis_config import get_redis_client, redis, redis_settings

security = HTTPBearer(auto_error=False)


async def get_session_repository(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> RedisSessionRepository:
    return RedisSessionRepository(
        redis_client=redis_client, key_prefix=redis_settings.REDIS_SESSION_PREFIX
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
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
        refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS,
    )


def get_signup_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    session_repository: Annotated[SessionRepository, Depends(get_session_repository)],
) -> SignUpUseCase:
    """
    Dependency for SignUpUseCase.
    Injects all required dependencies.
    """
    return SignUpUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
        session_repository=session_repository,
        refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    )


def get_login_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    session_repository: Annotated[SessionRepository, Depends(get_session_repository)],
) -> LoginUseCase:
    """
    Dependency for LoginUseCase.
    Injects all required dependencies.
    """
    return LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
        refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
        session_repository=session_repository,
    )


def get_logout_use_case(
    token_service: Annotated[TokenService, Depends(get_token_service)],
    session_repository: Annotated[SessionRepository, Depends(get_session_repository)],
) -> LogoutUseCase:
    """
    Dependency for LogoutUseCase.
    Injects all required dependencies.
    """
    return LogoutUseCase(
        token_service=token_service, session_repository=session_repository
    )


def get_refresh_token_use_case(
    token_service: Annotated[TokenService, Depends(get_token_service)],
    session_repository: Annotated[SessionRepository, Depends(get_session_repository)],
) -> RefreshTokenUseCase:
    """
    Dependency for RefreshTokenUseCase.
    Injects all required dependencies.
    """
    return RefreshTokenUseCase(
        session_repository=session_repository,
        token_service=token_service,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    )


def get_update_user_profile_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserProfileUseCase:
    """
    Dependency for UpdateUserProfileUseCase.
    Injects all required dependencies.
    """
    return UpdateUserProfileUseCase(user_repository=user_repository)


def get_get_user_profile_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserProfileUseCase:
    """
    Dependency for GetUserProfileUseCase.
    Injects all required dependencies.
    """
    return GetUserProfileUseCase(user_repository=user_repository)


# Application dependencies
GetUserProfileUseCaseDep = Annotated[
    GetUserProfileUseCase, Depends(get_get_user_profile_use_case)
]
UpdateUserProfileUseCaseDep = Annotated[
    UpdateUserProfileUseCase, Depends(get_update_user_profile_use_case)
]

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
SignUpUseCaseDep = Annotated[SignUpUseCase, Depends(get_signup_use_case)]
LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
RefreshTokenUseCaseDep = Annotated[
    RefreshTokenUseCase, Depends(get_refresh_token_use_case)
]
