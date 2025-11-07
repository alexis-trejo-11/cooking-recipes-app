from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .user import User, UserId


class UserRepository(ABC):
    """Abstract base class for User repository"""

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user (create or update)"""
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        pass

    @abstractmethod
    async def exists_by_id(self, user_id: UserId) -> bool:
        """Check if user exists by user_id"""
        pass


class PasswordHasher(ABC):
    """Abstract base class for password hashing"""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash a password"""
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        pass


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
