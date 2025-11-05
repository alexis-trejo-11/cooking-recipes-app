from fastapi import APIRouter, HTTPException, status
from app.auth.application.auth_use_cases import (
    SignUpRequest,
    LoginRequest,
    AuthResponse,
)
from .depencies import SignUpUseCaseDep, LoginUseCaseDep
from app.auth.application.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create a new user account and return authentication tokens",
)
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
    try:
        result = await use_case.execute(request)
        return result

    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User Login",
    description="Authenticate user and return access token",
)
async def login(
    request: LoginRequest,
    use_case: LoginUseCaseDep,
) -> AuthResponse:
    """
    Authenticate user and return JWT token.

    - **email**: User's email address
    - **password**: User's password
    """
    try:
        result = await use_case.execute(request)
        return result
    except (InvalidCredentialsException, UserNotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )
