from .base import SecurityException, ServerException, ApplicationException
from typing import Optional, Dict, Any

HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403


class AuthenticationException(SecurityException):
    """Base exception for authentication-related errors"""

    def __init__(
        self,
        message: str = "Authentication error occurred",
        error_code: str = "AUTHENTICATION_ERROR",
        status_code: int = HTTP_401_UNAUTHORIZED,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class ForbiddenException(SecurityException):
    """Base exception for forbidden access errors"""

    def __init__(
        self,
        message: str = "Security error occurred",
        error_code: str = "FORBIDDEN_ERROR",
        status_code: int = HTTP_403_FORBIDDEN,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class AuthAppException(ApplicationException):
    """Base exception for authentication application errors"""

    def __init__(
        self,
        message: str = "Authentication application error occurred",
        error_code: str = "AUTH_APPLICATION_ERROR",
        status_code: int = HTTP_422_UNPROCESSABLE_ENTITY,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class UserException(ApplicationException):
    """Base exception for user-related errors"""

    def __init__(
        self,
        message: str = "User operation failed",
        error_code: str = "USER_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message, error_code, HTTP_422_UNPROCESSABLE_ENTITY, details, context
        )


class RecipeException(ApplicationException):
    """Base exception for recipe-related errors"""

    def __init__(
        self,
        message: str = "Recipe operation failed",
        error_code: str = "RECIPE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message, error_code, HTTP_422_UNPROCESSABLE_ENTITY, details, context
        )


class MappingException(ServerException):
    """Base exception for mapping-related errors"""

    def __init__(
        self,
        message: str = "Mapping operation failed",
        error_code: str = "MAPPING_ERROR",
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message, error_code, HTTP_422_UNPROCESSABLE_ENTITY, details, context
        )


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
