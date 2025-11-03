from typing import Optional, List, Dict, Any


class UserException(Exception):
    """Base exception for all user-related errors."""

    pass


class UserValidationException(UserException):
    """Exception raised for user validation errors."""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation error for field '{field}': {message}")


class UserCreationException(UserException):
    """Exception raised when user creation fails."""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        self.errors = errors or []
        super().__init__(f"User creation failed: {message}")


class UserReconstructionException(UserException):
    """Exception raised when user reconstruction from data fails."""

    def __init__(self, message: str, invalid_data: Optional[Dict[str, Any]] = None):
        self.invalid_data = invalid_data or {}
        super().__init__(f"User reconstruction failed: {message}")


class UserUpdateException(UserException):
    """Exception raised when user update operations fail."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(f"User update failed: {message}")


class UserSecurityException(UserException):
    """Exception raised for security-related user operations."""

    def __init__(self, message: str, operation: Optional[str] = None):
        self.operation = operation
        super().__init__(f"Security violation: {message}")
