from abc import ABC, abstractmethod


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
