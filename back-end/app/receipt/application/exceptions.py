class ApplicationException(Exception):
    """Base exception for application layer errors"""

    pass


class AuthenticationException(ApplicationException):
    """Authentication related errors"""

    pass


class AuthorizationException(ApplicationException):
    """Authorization related errors"""

    pass


class UserNotFoundException(ApplicationException):
    """User not found errors"""

    pass


class UserAlreadyExistsException(ApplicationException):
    """User already exists errors"""

    pass


class InvalidCredentialsException(AuthenticationException):
    """Invalid credentials errors"""

    pass


class InvalidTokenException(AuthenticationException):
    """Invalid token errors"""

    pass


class RecipeNotFoundException(ApplicationException):
    """Recipe not found errors"""

    pass


class RecipeDomainException(ApplicationException):
    """Base exception for recipe domain errors"""

    pass


class RecipeValidationException(RecipeDomainException):
    """Recipe validation errors"""

    pass
