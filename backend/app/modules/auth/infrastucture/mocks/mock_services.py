from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt
from jwt.exceptions import InvalidTokenError
from app.modules.auth.domain.interfaces import EnhancedTokenService, PasswordHasher
from app.modules.auth.domain.user import User
from app.modules.auth.application.exceptions import (
    InvalidTokenException,
    UserNotFoundException,
)


class MockPasswordHasher(PasswordHasher):
    """Mock implementation of PasswordHasher for testing"""

    async def hash_password(self, password: str) -> str:
        return f"hashed_{password}"

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{plain_password}"


class MockTokenService(EnhancedTokenService):
    """Mock implementation of EnhancedTokenService for testing"""

    def __init__(self, secret_key: str = "test-secret-key", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self._user_store = {}

    async def create_tokens(self, user: User) -> Tuple[str, str]:
        access = await self.create_access_token(user)
        refresh = await self.create_refresh_token(user)
        return access, refresh

    async def create_access_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id.value),
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self._user_store[token] = user
        return token

    async def create_refresh_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id.value),
            "email": user.email,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self._user_store[token] = user
        return token

    async def verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                raise InvalidTokenException("Token is not an access token")
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")

    async def verify_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                raise InvalidTokenException("Token is not a refresh token")
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")

    async def get_user_from_token(self, token: str) -> User:
        user = self._user_store.get(token)
        if not user:
            raise UserNotFoundException("User not found for token")
        return user

    async def get_user_from_refresh_token(self, token: str) -> User:
        return await self.get_user_from_token(token)
