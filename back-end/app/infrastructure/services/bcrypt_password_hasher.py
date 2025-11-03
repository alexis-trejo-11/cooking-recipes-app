from passlib.context import CryptContext
from app.application.interfaces.password_hasher import PasswordHasher


class BCryptPasswordHasher(PasswordHasher):
    """Real password hasher using bcrypt for production"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its bcrypt hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
