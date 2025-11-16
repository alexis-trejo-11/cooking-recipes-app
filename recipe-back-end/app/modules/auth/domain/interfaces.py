from abc import ABC, abstractmethod
from typing import Optional, List, Protocol, Tuple
from .user import User, UserId, UserRecipeStats
from .session import UserSession


class UserRepository(ABC):
    """Abstract base class for User repository"""

    @abstractmethod
    async def get_by_id(self, id: UserId) -> Optional[User]:
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
    async def delete(self, id: UserId) -> bool:
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
    async def exists_by_id(self, id: UserId) -> bool:
        """Check if user exists by id"""
        pass

    @abstractmethod
    async def get_recipe_stats(self, id: UserId) -> UserRecipeStats:
        """Get user statistics"""
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


class EnhancedTokenService(Protocol):
    """Enhanced token service with refresh token support"""

    async def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create both access and refresh tokens

        Returns:
            Tuple[access_token, refresh_token]
        """
        ...

    async def create_access_token(self, user: User) -> str:
        """Create JWT access token (short-lived)"""
        ...

    async def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token (long-lived)"""
        ...

    async def verify_access_token(self, token: str) -> dict:
        """Verify access token and return payload"""
        ...

    async def verify_refresh_token(self, token: str) -> dict:
        """Verify refresh token and return payload"""
        ...

    async def get_user_from_token(self, token: str) -> User:
        """Get user from access token"""
        ...

    async def get_user_from_refresh_token(self, token: str) -> User:
        """Get user from refresh token"""
        ...


class SessionRepository(Protocol):
    """Repository interface for session management"""

    async def save_session(self, session: UserSession) -> None:
        """Save a new session"""
        ...

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        ...

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[UserSession]:
        """Get session by refresh token"""
        ...

    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        ...

    async def delete_all_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user (logout from all devices)"""
        ...

    async def update_last_activity(self, session_id: str) -> None:
        """Update session last activity timestamp"""
        ...

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        ...
