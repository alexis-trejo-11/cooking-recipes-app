import bcrypt
from app.auth.domain.interfaces import PasswordHasher


class BCryptPasswordHasher(PasswordHasher):
    """BCrypt password hasher implementation"""

    async def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        Automatically handles password truncation to 72 bytes.
        """
        # Convert to bytes and hash
        password_bytes = password.encode("utf-8")

        # BCrypt automatically truncates to 72 bytes to avoid warning
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its bcrypt hash.
        """
        try:
            plain_bytes = plain_password.encode("utf-8")

            # Truncate if necessary for verification
            if len(plain_bytes) > 72:
                plain_bytes = plain_bytes[:72]

            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            return False
