from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.modules.auth.domain.interfaces import TokenService, UserRepository
from app.modules.auth.domain.user import User, UserId
from app.modules.auth.application.exceptions import (
    InvalidTokenException,
    UserNotFoundException,
)


class JWTTokenService(TokenService):
    """Real JWT token service implementation for production"""

    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    async def create_access_token(self, user: User) -> str:
        """Create JWT access token for user"""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expiration_time = datetime.now(timezone.utc) + expires_delta
        issued_at = datetime.now(timezone.utc)

        payload = {
            "sub": str(user.user_id.value),
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "exp": expiration_time,
            "iat": issued_at,
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def verify_access_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise InvalidTokenException("Token has expired")

            return payload

        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")

    async def get_user_from_token(self, token: str) -> User:
        """Get user from JWT token"""
        payload = await self.verify_access_token(token)
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
