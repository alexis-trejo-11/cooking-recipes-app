from typing import Any, Dict
from app.utils.core.exceptions.modules import AuthAppException


class UserAlreadyExistsException(AuthAppException):
    """Exception raised when a user already exists."""

    def __init__(
        self,
        message: str = "User already exists.",
        error_code: str = "USER_ALREADY_EXISTS",
        status_code: int = 409,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class InvalidCredentialsException(AuthAppException):
    """Exception raised for invalid user credentials."""

    def __init__(
        self,
        message: str = "Invalid credentials provided.",
        error_code: str = "INVALID_CREDENTIALS",
        status_code: int = 401,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class InvalidTokenException(AuthAppException):
    """Invalid token exception"""

    def __init__(
        self,
        message: str = "Invalid authentication token",
        error_code: str = "INVALID_TOKEN",
        status_code: int = 401,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class UserNotFoundException(AuthAppException):
    """User not found exception"""

    def __init__(
        self,
        message: str = "User not found",
        error_code: str = "USER_NOT_FOUND",
        status_code: int = 404,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class InsufficientPermissionsError(AuthAppException):
    """User doesn't have required permissions"""

    def __init__(
        self,
        message: str = "Authentication application error occurred",
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        status_code: int = 403,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class MissingTokenError(AuthAppException):
    """Missing authentication token"""

    def __init__(
        self,
        message: str = "Authentication token is missing",
        error_code: str = "MISSING_TOKEN",
        status_code: int = 401,
        details: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code, status_code, details, context)
