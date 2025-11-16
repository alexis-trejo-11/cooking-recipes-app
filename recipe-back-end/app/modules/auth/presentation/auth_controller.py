from fastapi import APIRouter, status, Header, Query, Request
from typing import Annotated
from app.modules.auth.application.auth_use_cases import (
    SignUpRequest,
    LoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    LogoutResponse,
    UserResponse,
)
from .app_depencies import (
    SignUpUseCaseDep,
    LoginUseCaseDep,
    RefreshTokenUseCaseDep,
    LogoutUseCaseDep,
)
from .auth_depencies import CurrentUser
from app.config.rate_limiter import rate_limit
from app.modules.auth.application.exceptions import InvalidTokenException

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create a new user account and return authentication tokens",
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        422: {"description": "Validation error or user already exists"},
    },
)
@rate_limit("strict")
async def signup(
    request: Request,
    signup_request: SignUpRequest,
    use_case: SignUpUseCaseDep,
) -> AuthResponse:
    """
    Register a new user and create a session.

    **Request Body:**
    - **first_name**: User's first name (2-50 characters)
    - **last_name**: User's last name (2-50 characters)
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **phone_number**: Optional phone number in international format
    - **gender**: User's gender
    - **date_of_birth**: User's date of birth

    **Returns:**
    - **access_token**: Short-lived JWT token (30 minutes) for API requests
    - **refresh_token**: Long-lived JWT token (7 days) for obtaining new access tokens
    - **token_type**: Always "bearer"
    - **expires_in**: Access token expiration time in seconds
    - **user_id**: Unique identifier for the created user
    """
    device_info = extract_device_info(request)
    result = await use_case.execute(
        signup_request,
        device_info=device_info.get("device_info"),
        ip_address=device_info.get("ip_address"),
        user_agent=device_info.get("user_agent"),
    )
    return result


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User Login",
    description="Authenticate user and return access and refresh tokens",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
@rate_limit("strict")
async def login(
    request: Request,
    login_request: LoginRequest,
    use_case: LoginUseCaseDep,
) -> AuthResponse:
    """
    Authenticate user and create a new session.

    **Request Body:**
    - **email**: User's email address
    - **password**: User's password

    **Returns:**
    - **access_token**: Short-lived JWT token for API requests
    - **refresh_token**: Long-lived JWT token for obtaining new access tokens
    - **token_type**: Always "bearer"
    - **expires_in**: Access token expiration time in seconds
    - **user_id**: Unique identifier for the user

    **Security:**
    - Rate limited to prevent brute force attacks
    - Failed login attempts are logged
    - Passwords are never stored in plain text
    """
    device_info = extract_device_info(request)
    result = await use_case.execute(
        login_request,
        device_info=device_info.get("device_info"),
        ip_address=device_info.get("ip_address"),
        user_agent=device_info.get("user_agent"),
    )
    return result


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh Access Token",
    description="Get a new access token using a valid refresh token",
    responses={
        200: {
            "description": "New access token generated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        401: {"description": "Invalid or expired refresh token"},
    },
)
@rate_limit("moderate")
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    use_case: RefreshTokenUseCaseDep,
) -> AuthResponse:
    """
    Refresh access token using a valid refresh token.

    **Request Body:**
    - **refresh_token**: Valid refresh token received during login/signup

    **Returns:**
    - **access_token**: New short-lived JWT token
    - **refresh_token**: Same refresh token (not rotated)
    - **token_type**: Always "bearer"
    - **expires_in**: Access token expiration time in seconds
    - **user_id**: User identifier

    **Notes:**
    - Access tokens expire after 30 minutes
    - Refresh tokens expire after 7 days
    - Use this endpoint when you get a 401 error with "Token has expired"
    - The session must still be valid (not logged out)
    """
    result = await use_case.execute(refresh_request)
    return result


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout User",
    description="Revoke refresh token and end session",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Successfully logged out",
                        "revoked_sessions": 1,
                    }
                }
            },
        },
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def logout(
    refresh_request: RefreshTokenRequest,
    use_case: LogoutUseCaseDep,
    logout_all: bool = Query(
        False,
        description="If true, logout from all devices. If false, logout only from current device.",
    ),
) -> LogoutResponse:
    """
    Logout user by revoking session(s).

    **Request Body:**
    - **refresh_token**: Valid refresh token to revoke

    **Query Parameters:**
    - **logout_all**: If true, revokes all sessions (logout from all devices)

    **Returns:**
    - **message**: Success message
    - **revoked_sessions**: Number of sessions that were revoked

    **Notes:**
    - After logout, both access and refresh tokens become invalid
    - Use `logout_all=true` to logout from all devices (e.g., for security reasons)
    - The refresh token will be removed from Redis immediately
    """
    result = await use_case.execute(
        refresh_token=refresh_request.refresh_token, logout_all_devices=logout_all
    )
    return result


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user's profile",
    responses={
        200: {
            "description": "User profile",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "phone_number": "+1234567890",
                        "roles": ["common_user"],
                        "is_active": True,
                        "joined_at": "2025-01-15T10:30:00Z",
                        "last_login": "2025-11-16T08:45:00Z",
                    }
                }
            },
        },
        401: {"description": "Invalid or expired access token"},
    },
)
async def get_current_user(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get current authenticated user's profile.

    **Headers:**
    - **Authorization**: Bearer {access_token}

    **Returns:**
    User profile information including:
    - Basic info (name, email, phone)
    - Roles and permissions
    - Account status
    - Registration and last login dates

    **Security:**
    - Requires valid access token
    - Only returns information for the authenticated user
    """
    # Extract token from "Bearer {token}"
    return UserResponse.from_user(current_user)


@router.get(
    "/sessions",
    summary="List Active Sessions",
    description="List all active sessions for the current user (Optional - implement if needed)",
    include_in_schema=False,  # Hide from docs until implemented
)
async def list_sessions():
    """
    List all active sessions for the current user.

    This endpoint would show:
    - Device information
    - IP addresses
    - Last activity
    - Creation time

    Implementation left as exercise (requires additional use case)
    """
    return {"message": "Not implemented yet"}


@router.delete(
    "/sessions/{session_id}",
    summary="Revoke Specific Session",
    description="Revoke a specific session by ID (Optional - implement if needed)",
    include_in_schema=False,  # Hide from docs until implemented
)
async def revoke_session(session_id: str):
    """
    Revoke a specific session by its ID.

    Useful for:
    - Remotely logging out a specific device
    - Revoking suspicious sessions

    Implementation left as exercise (requires additional use case)
    """
    return {"message": "Not implemented yet"}


def extract_device_info(request: Request) -> dict:
    """Extract device information from request"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "device_info": request.headers.get("x-device-info"),  # Optional custom header
    }
