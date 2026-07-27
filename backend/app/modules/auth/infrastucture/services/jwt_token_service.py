from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.modules.auth.domain.interfaces import EnhancedTokenService, UserRepository
from app.modules.auth.domain.user import User, UserId
from app.modules.auth.application.exceptions import (
    InvalidTokenException,
    UserNotFoundException,
)
from typing import Tuple
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
import secrets


class JWTTokenService(EnhancedTokenService):
    """Enhanced JWT token service with refresh token support"""

    def __init__(
        self,
        refresh_token_expire_days: int,
        access_token_expire_minutes: int,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str = "HS256",
    ):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    async def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create both access and refresh tokens"""
        access_token = await self.create_access_token(user)
        refresh_token = await self.create_refresh_token(user)
        return access_token, refresh_token

    async def create_access_token(self, user: User) -> str:
        """Create short-lived JWT access token"""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expiration_time = datetime.now(timezone.utc) + expires_delta
        issued_at = datetime.now(timezone.utc)

        payload = {
            "sub": str(user.id.value),
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "exp": expiration_time,
            "iat": issued_at,
            "type": "access",
            "jti": secrets.token_urlsafe(16),  # JWT ID for tracking
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user: User) -> str:
        """Create long-lived JWT refresh token"""
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        expiration_time = datetime.now(timezone.utc) + expires_delta
        issued_at = datetime.now(timezone.utc)

        payload = {
            "sub": str(user.id.value),
            "exp": expiration_time,
            "iat": issued_at,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16),  # JWT ID for session tracking
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def verify_access_token(self, token: str) -> dict:
        """Verify JWT access token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("type") != "access":
                raise InvalidTokenException("Invalid token type")

            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise InvalidTokenException("Token has expired")

            return payload

        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid access token: {str(e)}")

    async def verify_refresh_token(self, token: str) -> dict:
        """Verify JWT refresh token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("type") != "refresh":
                raise InvalidTokenException("Invalid token type")

            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise InvalidTokenException("Refresh token has expired")

            return payload

        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid refresh token: {str(e)}")

    async def get_user_from_token(self, token: str) -> User:
        """Get user from JWT access token"""
        payload = await self.verify_access_token(token)
        return await self._get_user_from_payload(payload)

    async def get_user_from_refresh_token(self, token: str) -> User:
        """Get user from JWT refresh token"""
        payload = await self.verify_refresh_token(token)
        return await self._get_user_from_payload(payload)

    async def _get_user_from_payload(self, payload: dict) -> User:
        """Helper to extract user from token payload"""
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise InvalidTokenException("Token missing subject")

        try:
            user_id = UserId.from_string(user_id_str)
        except (ValueError, AttributeError):
            raise InvalidTokenException("Invalid user ID in token")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")

        return user
