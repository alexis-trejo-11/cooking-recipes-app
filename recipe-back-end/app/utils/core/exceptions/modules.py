# app/core/exceptions/modules.py
from .base import ClientException, ServerException
from typing import Optional, Dict, Any


class AuthenticationException(ClientException):
    """Base exception for authentication-related errors"""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 401, details, context)


class ForbiddenException(ClientException):
    """Base exception for forbidden access errors"""

    def __init__(
        self,
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 403, details, context)


class UserException(ClientException):
    """Base exception for user-related errors"""

    def __init__(
        self,
        message: str = "User operation failed",
        error_code: str = "USER_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 400, details, context)


class RecipeException(ClientException):
    """Base exception for recipe-related errors"""

    def __init__(
        self,
        message: str = "Recipe operation failed",
        error_code: str = "RECIPE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 400, details, context)


class DatabaseException(ServerException):
    """Base exception for database-related errors"""

    def __init__(
        self,
        message: str = "Database operation failed",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 500, details, context)


class ExternalServiceException(ServerException):
    """Base exception for external service errors"""

    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, 502, details, context)
