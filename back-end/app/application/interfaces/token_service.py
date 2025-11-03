from abc import ABC, abstractmethod
from typing import Dict, Any
from app.domain.entities.user import User


class TokenService(ABC):
    """Abstract base class for token generation and verification"""

    @abstractmethod
    async def create_access_token(self, user: User) -> str:
        """Create access token for user"""
        pass

    @abstractmethod
    async def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify access token and return payload"""
        pass

    @abstractmethod
    async def get_user_from_token(self, token: str) -> User:
        """Get user from token"""
        pass
