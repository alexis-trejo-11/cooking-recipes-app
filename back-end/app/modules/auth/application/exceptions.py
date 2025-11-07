class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists."""

    pass


class InvalidCredentialsException(Exception):
    """Exception raised for invalid user credentials."""

    pass


class AuthenticationError(Exception):
    """Base authentication exception"""

    pass


class InvalidTokenException(AuthenticationError):
    """Invalid token exception"""

    pass


class UserNotFoundException(AuthenticationError):
    """User not found exception"""

    pass


class InsufficientPermissionsError(AuthenticationError):
    """User doesn't have required permissions"""

    pass


class MissingTokenError(AuthenticationError):
    """Missing authentication token"""

    pass
