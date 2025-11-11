from fastapi import APIRouter, status
from app.modules.auth.application.auth_use_cases import (
    SignUpRequest,
    LoginRequest,
    AuthResponse,
)
from .app_depencies import SignUpUseCaseDep, LoginUseCaseDep
from app.config.rate_limiter import rate_limit

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create a new user account and return authentication tokens",
)
@rate_limit("strict")
async def signup(
    request: SignUpRequest,
    use_case: SignUpUseCaseDep,
) -> AuthResponse:
    """
    Register a new user.

    - **first_name**: User's first name (2-50 characters)
    - **last_name**: User's last name (2-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **phone_number**: Optional phone number in international format
    """
    result = await use_case.execute(request)
    return result


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User Login",
    description="Authenticate user and return access token",
)
@rate_limit("strict")
async def login(
    request: LoginRequest,
    use_case: LoginUseCaseDep,
) -> AuthResponse:
    """
    Authenticate user and return JWT token.

    - **email**: User's email address
    - **password**: User's password
    """
    result = await use_case.execute(request)
    return result
