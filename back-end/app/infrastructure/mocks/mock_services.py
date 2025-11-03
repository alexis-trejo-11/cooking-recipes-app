from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.application.interfaces.password_hasher import PasswordHasher
from app.application.interfaces.token_service import TokenService
from app.domain.entities.user import User
from app.application.exceptions import InvalidTokenException, UserNotFoundException


class MockPasswordHasher(PasswordHasher):
    """Mock implementation of PasswordHasher for testing"""

    async def hash_password(self, password: str) -> str:
        return f"hashed_{password}"

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{plain_password}"


class MockTokenService(TokenService):
    """Mock implementation of TokenService for testing"""

    def __init__(self, secret_key: str = "test-secret-key", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self._user_store = {}  # token -> user mapping for testing

    async def create_access_token(self, user: User) -> str:
        payload = {
            "sub": str(user.user_id),
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self._user_store[token] = user
        return token

    async def verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")

    async def get_user_from_token(self, token: str) -> User:
        user = self._user_store.get(token)
        if not user:
            raise UserNotFoundException("User not found for token")
        return user
