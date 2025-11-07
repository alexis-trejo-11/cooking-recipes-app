from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.modules.auth.application.exceptions import (
    AuthenticationError,
    InvalidTokenException,
    UserNotFoundException,
    InsufficientPermissionsError,
    MissingTokenError,
)


async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication exceptions"""
    status_code = status.HTTP_401_UNAUTHORIZED

    if isinstance(exc, InsufficientPermissionsError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, MissingTokenError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, (InvalidTokenException, UserNotFoundException)):
        status_code = status.HTTP_401_UNAUTHORIZED

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
