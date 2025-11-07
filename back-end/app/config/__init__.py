# app/core/exceptions/__init__.py
from app.utils.core.exceptions.base import (
    BaseAppException,
    ClientException,
    ServerException,
)
from app.utils.core.exceptions.modules import (
    AuthenticationException,
    ForbiddenException,
    UserException,
    RecipeException,
    DatabaseException,
    ExternalServiceException,
)
from .global_exception_handler import GlobalExceptionHandler

__all__ = [
    "BaseAppException",
    "ClientException",
    "ServerException",
    "AuthenticationException",
    "ForbiddenException",
    "UserException",
    "RecipeException",
    "DatabaseException",
    "ExternalServiceException",
    # ADD SPECIFIC EXCEPTIONS HERE
    "InvalidTokenException",
    "MissingTokenException",
    "InsufficientPermissionsException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCredentialsException",
    "RecipeNotFoundException",
    "RecipeAccessDeniedException",
    "DatabaseConnectionException",
    "UniqueConstraintException",
    "GlobalExceptionHandler",
]
