from typing import Optional
from ..dto.auth_dtos import (
    SignUpRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
)
from ..interfaces.user_repository import UserRepository
from ..interfaces.password_hasher import PasswordHasher
from app.application.interfaces.token_service import TokenService
from app.application.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.domain.entities.user import User, UserRole, UserId
from app.domain.exceptions.user_exceptions import UserCreationException


class SignUpUseCase:
    """Use case for user registration"""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def execute(self, request: SignUpRequest) -> AuthResponse:
        """Execute user registration"""
        if await self.user_repository.exists_by_email(request.email):
            raise UserAlreadyExistsException(
                f"User with email {request.email} already exists"
            )

        try:
            user = User.create(
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                raw_password=request.password,
                phone_number=request.phone_number,
                roles=[UserRole.COMMON_USER],
            )

            hashed_password = await self.password_hasher.hash_password(request.password)
            user.set_hashed_password(hashed_password)

            saved_user = await self.user_repository.save(user)

            access_token = await self.token_service.create_access_token(saved_user)

            return AuthResponse(
                access_token=access_token,
                user_id=str(saved_user.user_id),
                email=saved_user.email,
                first_name=saved_user.first_name,
                last_name=saved_user.last_name,
                roles=[role.value for role in saved_user.roles],
            )

        except UserCreationException as e:
            raise InvalidCredentialsException(f"Invalid user data: {str(e)}") from e


class LoginUseCase:
    """Use case for user login"""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def execute(self, request: LoginRequest) -> AuthResponse:
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

        access_token = await self.token_service.create_access_token(user)

        return AuthResponse(
            access_token=access_token,
            user_id=str(user.user_id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=[role.value for role in user.roles],
        )


class GetCurrentUserUseCase:
    """Use case to get current user from token"""

    def __init__(self, user_repository: UserRepository, token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def execute(self, token: str) -> UserResponse:
        """Execute get current user"""

        user = await self.token_service.get_user_from_token(token)

        if not user:
            raise UserNotFoundException("User not found")

        return UserResponse(
            user_id=str(user.user_id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            roles=[role.value for role in user.roles],
            is_active=user.is_active,
            joined_at=user.joined_at,
            last_login=user.last_login,
        )
