import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.modules.auth.domain.user import User, UserRole, UserGender
from app.modules.auth.domain.session import UserSession
from app.modules.auth.application.exceptions import InvalidTokenException
from app.modules.auth.domain.exceptions import UserCreationException
from app.modules.auth.domain.interfaces import (
    UserRepository,
    SessionRepository,
    PasswordHasher,
    EnhancedTokenService as JWTTokenService,
)
from .dtos import (
    SignUpRequest,
    LoginRequest,
    RefreshTokenRequest,
    LogoutResponse,
    AuthResponse,
    UserResponse,
)
from .exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)

logger = logging.getLogger(__name__)


class SignUpUseCase:
    """Use case for user registration with session management"""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: JWTTokenService,
        session_repository: SessionRepository,
        refresh_token_expire_days: int = 30,
        access_token_expire_minutes: int = 15,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.session_repository = session_repository
        self.refresh_token_expire_days = refresh_token_expire_days
        self.access_token_expire_minutes = access_token_expire_minutes

    async def execute(
        self,
        request: SignUpRequest,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthResponse:
        """Execute user registration"""
        logger.info(f"Attempting to sign up user: {request.email}")
        logger.debug(f"Request details: {request.model_dump()}")

        if await self.user_repository.exists_by_email(request.email):
            raise UserAlreadyExistsException(
                f"User with email {request.email} already exists"
            )

        if request.phone_number:
            if await self.user_repository.exists_by_phone(request.phone_number):
                raise UserAlreadyExistsException(
                    f"User with phone number {request.phone_number} already exists"
                )

        try:
            user = User.create(
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                raw_password=request.password,
                phone_number=request.phone_number,
                roles=[UserRole.COMMON_USER],
                gender=UserGender(request.gender),
                date_of_birth=request.date_of_birth,
            )

            hashed_password = await self.password_hasher.hash_password(request.password)
            user.set_hashed_password(hashed_password)

            saved_user = await self.user_repository.save(user)

            # Create tokens
            access_token, refresh_token = await self.token_service.create_tokens(
                saved_user
            )

            # Create session
            session = UserSession(
                session_id=secrets.token_urlsafe(32),
                user_id=str(saved_user.id.value),
                refresh_token=refresh_token,
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=self.refresh_token_expire_days),
                last_activity=datetime.now(timezone.utc),
            )

            await self.session_repository.save_session(session)

            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60,
                user_id=str(saved_user.id.value),
            )

        except UserCreationException as e:
            raise InvalidCredentialsException(f"Invalid user data: {str(e)}") from e


class LoginUseCase:
    """Use case for user login with session management"""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: JWTTokenService,
        session_repository: SessionRepository,
        refresh_token_expire_days: int,
        access_token_expire_minutes: int,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.session_repository = session_repository
        self.refresh_token_expire_days = refresh_token_expire_days
        self.access_token_expire_minutes = access_token_expire_minutes

    async def execute(
        self,
        request: LoginRequest,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthResponse:
        """Execute user login"""

        user = await self.user_repository.get_by_email(request.email)
        if not user:
            raise InvalidCredentialsException("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsException("User account is deactivated")

        is_valid_password = await self.password_hasher.verify_password(
            request.password, user.password
        )
        if not is_valid_password:
            raise InvalidCredentialsException("Invalid email or password")

        user.record_login()
        await self.user_repository.save(user)

        # Create tokens
        access_token, refresh_token = await self.token_service.create_tokens(user)

        # Create session
        session = UserSession(
            session_id=secrets.token_urlsafe(32),
            user_id=str(user.id.value),
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
            last_activity=datetime.now(timezone.utc),
        )

        await self.session_repository.save_session(session)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user_id=str(user.id.value),
        )


class RefreshTokenUseCase:
    """Use case to refresh access token"""

    def __init__(
        self,
        token_service: JWTTokenService,
        session_repository: SessionRepository,
        access_token_expire_minutes: int,
    ):
        self.token_service = token_service
        self.session_repository = session_repository
        self.access_token_expire_minutes = access_token_expire_minutes

    async def execute(self, request: RefreshTokenRequest) -> AuthResponse:
        """Execute token refresh"""

        user = await self.token_service.get_user_from_refresh_token(
            request.refresh_token
        )

        session = await self.session_repository.get_session_by_refresh_token(
            request.refresh_token
        )

        if not session:
            raise InvalidTokenException("Invalid or expired refresh token")

        # Check if session is expired
        if session.expires_at < datetime.now(timezone.utc):
            await self.session_repository.delete_session(session.session_id)
            raise InvalidTokenException("Session has expired")

        # Create new access token (keep same refresh token)
        access_token = await self.token_service.create_access_token(user)

        # Update session activity
        await self.session_repository.update_last_activity(session.session_id)

        return AuthResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user_id=str(user.id.value),
        )


class LogoutUseCase:
    """Use case to logout user"""

    def __init__(
        self,
        token_service: JWTTokenService,
        session_repository: SessionRepository,
    ):
        self.token_service = token_service
        self.session_repository = session_repository

    async def execute(
        self, refresh_token: str, logout_all_devices: bool = False
    ) -> LogoutResponse:
        """Execute logout"""

        # Get user from refresh token
        user = await self.token_service.get_user_from_refresh_token(refresh_token)

        if logout_all_devices:
            # Logout from all devices
            revoked_count = await self.session_repository.delete_all_user_sessions(
                str(user.id.value)
            )
        else:
            # Logout from current device only
            session = await self.session_repository.get_session_by_refresh_token(
                refresh_token
            )
            if session:
                await self.session_repository.delete_session(session.session_id)
                revoked_count = 1
            else:
                revoked_count = 0

        return LogoutResponse(
            message="Successfully logged out", revoked_sessions=revoked_count
        )


class GetCurrentUserUseCase:
    """Use case to get current user from token"""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: JWTTokenService,
    ):
        self.user_repository = user_repository
        self.token_service = token_service

    async def execute(self, token: str) -> UserResponse:
        """Execute get current user"""

        user = await self.token_service.get_user_from_token(token)

        if not user:
            raise UserNotFoundException("User not found")

        return UserResponse(
            user_id=str(user.id.value),
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone_number=user.phone_number,
            roles=[role.value for role in user.roles],
            is_active=user.is_active,
            joined_at=user.joined_at,
            last_login=user.last_login,
        )
