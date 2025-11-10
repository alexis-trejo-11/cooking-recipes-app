from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Optional, List
from app.modules.auth.domain.interfaces import TokenService
from app.modules.auth.domain.user import User, UserRole
from app.modules.auth.application.exceptions import (
    InvalidTokenException,
    UserNotFoundException,
    InsufficientPermissionsError,
    MissingTokenError,
)
from app.utils.core.exceptions.modules import (
    AuthenticationException,
)

from .app_depencies import get_token_service

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    """
    Dependency to get current user from JWT token
    """
    if not credentials:
        raise MissingTokenError("Authentication token required")

    try:
        user = await token_service.get_user_from_token(credentials.credentials)
        if not user.is_active:
            raise AuthenticationException("User account is inactive")
        return user
    except (InvalidTokenException, UserNotFoundException) as e:
        raise AuthenticationException(str(e))


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user
    """
    if not current_user.is_active:
        raise AuthenticationException("Inactive user")
    return current_user


def require_roles(required_roles: List[UserRole]):
    """
    Factory function to create role-based dependencies
    """

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_any_role(required_roles):
            raise InsufficientPermissionsError(
                f"Required roles: {[role.value for role in required_roles]}"
            )
        return current_user

    return role_checker


async def require_admin_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency that requires admin role"""
    if not current_user.has_role(UserRole.ADMIN):
        raise InsufficientPermissionsError("Admin role required")
    return current_user


async def require_moderator_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency that requires moderator role"""
    if not current_user.has_role(UserRole.MODERATOR):
        raise InsufficientPermissionsError("Moderator role required")
    return current_user


async def require_user_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency that requires user role"""
    if not current_user.has_roles(
        [
            UserRole.COMMON_USER,
        ]
    ):
        raise InsufficientPermissionsError("User role required")
    return current_user


async def require_premium_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency that requires premium user role"""
    if not current_user.has_role(UserRole.PREMIUM_USER):
        raise InsufficientPermissionsError("Premium user role required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin_role)]
ModeratorUser = Annotated[User, Depends(require_moderator_role)]
CommonUser = Annotated[User, Depends(require_user_role)]
PremiumUser = Annotated[User, Depends(require_premium_user)]
