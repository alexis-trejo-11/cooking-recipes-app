from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User, UserId


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
