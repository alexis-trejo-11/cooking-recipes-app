class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists."""

    pass


class UserNotFoundException(Exception):
    """Exception raised when a user is not found."""

    pass


class InvalidCredentialsException(Exception):
    """Exception raised for invalid user credentials."""

    pass


class InvalidTokenException(Exception):
    """Exception raised for invalid or expired tokens."""

    pass
