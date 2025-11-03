from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import re
from .enums import UserRole
from ..exceptions.user_exceptions import *
from .value_objects import UserId


class User:
    """
    A class representing a user in the system.

    This class provides factory methods for creating and reconstructing users
    with comprehensive validation and security measures.

    Attributes:
        _user_id: Unique identifier for the user
        _first_name: User's first name
        _last_name: User's last name
        _email: User's email address
        _phone_number: User's phone number (optional)
        _password: User's password (hashed in production)
        _roles: List of roles assigned to the user
        _joined_at: Timestamp when user joined
        _last_login: Timestamp of last login
        _is_active: Whether the user account is active
    """

    def __init__(
        self,
        user_id: UserId,
        first_name: str,
        last_name: str,
        password: str,
        email: str,
        phone_number: Optional[str],
        roles: List[UserRole],
        joined_at: datetime,
        last_login: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a User instance.

        Note: This constructor is intended for internal use only.
        Use factory methods create() or reconstruct() instead.

        Args:
            first_name: User's first name
            last_name: User's last name
            password: User's password
            email: User's email address
            phone_number: User's phone number
            roles: List of user roles
            joined_at: Timestamp when user joined
            last_login: Timestamp of last login
            user_id: Unique user identifier

        Raises:
            UserValidationException: If any validation fails
        """
        self._user_id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._phone_number = phone_number
        self._password = password
        self._roles = roles
        self._joined_at = joined_at
        self._last_login = last_login
        self._is_active = True

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        raw_password: str,
        phone_number: Optional[str] = None,
        roles: Optional[List[UserRole]] = None,
    ) -> "User":
        """
        Factory method to create a new user with comprehensive validation.

        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
            raw_password: User's raw password (will be validated)
            phone_number: User's phone number (optional)
            roles: List of user roles (defaults to COMMON_USER)

        Returns:
            User: A new User instance

        Raises:
            UserCreationException: If user creation fails due to validation errors
            UserValidationException: If specific field validation fails
        """
        errors = []

        try:
            # Basic field validation
            if not first_name or not first_name.strip():
                raise UserValidationException(
                    "first_name", "First name cannot be empty"
                )

            if not last_name or not last_name.strip():
                raise UserValidationException("last_name", "Last name cannot be empty")

            if not email or not email.strip():
                raise UserValidationException("email", "Email cannot be empty")

            if not raw_password:
                raise UserValidationException("password", "Password cannot be empty")

            # Specific validations
            cls._validate_email(email)
            cls._validate_raw_password(raw_password)

            if phone_number:
                cls._validate_phone_number(phone_number)

            cls._validate_full_name(first_name.strip(), last_name.strip())

        except UserValidationException as e:
            errors.append(str(e))
            raise UserCreationException("Validation failed", errors) from e

        # Create user instance
        try:
            return cls(
                user_id=UserId(),  # DB will assign actual ID
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                email=email.strip().lower(),
                password=raw_password,  #  this should be hashed
                phone_number=phone_number.strip() if phone_number else None,
                roles=roles or [UserRole.COMMON_USER],
                joined_at=datetime.now(timezone.utc),
            )
        except Exception as e:
            raise UserCreationException(
                f"Unexpected error during creation: {str(e)}"
            ) from e

    @classmethod
    def reconstruct(cls, user_data: Dict[str, Any]) -> "User":
        """
        Reconstruct a User instance from persisted data.

        Args:
            user_data: Dictionary containing user data from persistence layer

        Returns:
            User: Reconstructed User instance

        Raises:
            UserReconstructionException: If reconstruction fails due to invalid data
        """
        try:
            # Validate required fields
            required_fields = [
                "first_name",
                "last_name",
                "email",
                "password",
                "roles",
                "joined_at",
            ]
            missing_fields = [
                field for field in required_fields if field not in user_data
            ]

            if missing_fields:
                raise UserReconstructionException(
                    f"Missing required fields: {missing_fields}", invalid_data=user_data
                )

            # Process roles
            roles = []
            for role in user_data["roles"]:
                try:
                    if isinstance(role, UserRole):
                        roles.append(role)
                    elif isinstance(role, str):
                        roles.append(UserRole(role))
                    else:
                        raise ValueError(f"Invalid role type: {type(role)}")
                except ValueError as e:
                    raise UserReconstructionException(
                        f"Invalid role value: {role}", invalid_data=user_data
                    ) from e

            # Process dates
            try:
                joined_at = user_data["joined_at"]
                if isinstance(joined_at, str):
                    joined_at = datetime.fromisoformat(joined_at)
                elif not isinstance(joined_at, datetime):
                    raise ValueError("joined_at must be datetime or ISO string")

                last_login = user_data.get("last_login")
                if last_login and isinstance(last_login, str):
                    last_login = datetime.fromisoformat(last_login)

            except (ValueError, TypeError) as e:
                raise UserReconstructionException(
                    f"Invalid date format: {str(e)}", invalid_data=user_data
                ) from e

            # Create reconstructed user
            return cls(
                user_id=user_data.get("user_id", UserId()),
                first_name=str(user_data["first_name"]),
                last_name=str(user_data["last_name"]),
                email=str(user_data["email"]),
                password=str(user_data["password"]),
                phone_number=user_data.get("phone_number"),
                roles=roles,
                joined_at=joined_at,
                last_login=last_login,
            )

        except (KeyError, ValueError, TypeError) as e:
            raise UserReconstructionException(
                f"Data reconstruction error: {str(e)}", invalid_data=user_data
            ) from e

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the user to a dictionary for persistence.

        Returns:
            Dict[str, Any]: Dictionary containing all user data
        """
        return {
            "user_id": self._user_id,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "email": self._email,
            "password": self._password,
            "phone_number": self._phone_number,
            "roles": [role.value for role in self._roles],
            "joined_at": self._joined_at.isoformat(),
            "last_login": self._last_login.isoformat() if self._last_login else None,
            "is_active": self._is_active,
        }

    def record_login(self) -> None:
        """Record the user's last login timestamp."""
        self._last_login = datetime.now(timezone.utc)

    def set_hashed_password(self, hashed_password: str) -> None:
        """
        Set the hashed password for the user.

        Args:
            hashed_password: The hashed password string

        Raises:
            UserSecurityException: If password doesn't meet security requirements
        """
        if not hashed_password or len(hashed_password) < 8:
            raise UserSecurityException(
                "Hashed password must be at least 8 characters long",
                operation="set_hashed_password",
            )
        self._password = hashed_password

    def update_email(self, new_email: str) -> None:
        """
        Update user's email address with validation.

        Args:
            new_email: The new email address

        Raises:
            UserUpdateException: If email update fails
            UserValidationException: If email validation fails
        """
        if not new_email or not new_email.strip():
            raise UserUpdateException("Email cannot be empty", field="email")

        new_email = new_email.strip().lower()
        if new_email == self._email:
            return

        try:
            self._validate_email(new_email)
            self._email = new_email
        except UserValidationException as e:
            raise UserUpdateException(str(e), field="email") from e

    def update_names(self, first_name: str, last_name: str) -> None:
        """
        Update user's first and last names with validation.

        Args:
            first_name: New first name
            last_name: New last name

        Raises:
            UserUpdateException: If name update fails
            UserValidationException: If name validation fails
        """
        if not first_name or not first_name.strip():
            raise UserUpdateException("First name cannot be empty", field="first_name")
        if not last_name or not last_name.strip():
            raise UserUpdateException("Last name cannot be empty", field="last_name")

        first_name = first_name.strip()
        last_name = last_name.strip()

        if first_name == self._first_name and last_name == self._last_name:
            return

        try:
            self._validate_full_name(first_name, last_name)
            self._first_name = first_name
            self._last_name = last_name
        except UserValidationException as e:
            raise UserUpdateException(str(e), field=e.field) from e

    def update_phone_number(self, phone_number: Optional[str]) -> None:
        """
        Update user's phone number with validation.

        Args:
            phone_number: New phone number (None to remove)

        Raises:
            UserUpdateException: If phone number update fails
            UserValidationException: If phone number validation fails
        """
        if not phone_number:
            self._phone_number = None
            return

        phone_number = phone_number.strip()
        if phone_number == self._phone_number:
            return

        try:
            self._validate_phone_number(phone_number)
            self._phone_number = phone_number
        except UserValidationException as e:
            raise UserUpdateException(str(e), field="phone_number") from e

    def add_role(self, role: UserRole) -> None:
        """
        Add a role to the user.

        Args:
            role: The role to add
        """
        if role not in self._roles:
            self._roles.append(role)

    def remove_role(self, role: UserRole) -> None:
        """
        Remove a role from the user.

        Args:
            role: The role to remove
        """
        if role in self._roles:
            self._roles.remove(role)
        # Ensure user always has at least COMMON_USER role
        if not self._roles:
            self._roles.append(UserRole.COMMON_USER)

    def has_role(self, role: UserRole) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: The role to check

        Returns:
            bool: True if user has the role, False otherwise
        """
        return role in self._roles

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self._is_active = False

    def activate(self) -> None:
        """Activate the user account."""
        self._is_active = True

    # Property definitions
    @property
    def user_id(self) -> UserId:
        """Get the user's unique identifier."""
        return self._user_id

    @property
    def first_name(self) -> str:
        """Get the user's first name."""
        return self._first_name

    @property
    def last_name(self) -> str:
        """Get the user's last name."""
        return self._last_name

    @property
    def email(self) -> str:
        """Get the user's email address."""
        return self._email

    @property
    def phone_number(self) -> Optional[str]:
        """Get the user's phone number."""
        return self._phone_number

    @property
    def password(self) -> str:
        """Get the user's password (hashed in production)."""
        return self._password

    @property
    def roles(self) -> List[UserRole]:
        """Get a copy of the user's roles."""
        return self._roles.copy()

    @property
    def joined_at(self) -> datetime:
        """Get the timestamp when user joined."""
        return self._joined_at

    @property
    def last_login(self) -> Optional[datetime]:
        """Get the timestamp of last login."""
        return self._last_login

    @property
    def is_active(self) -> bool:
        """Check if the user account is active."""
        return self._is_active

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return f"{self._first_name} {self._last_name}"

    # Validation methods
    @staticmethod
    def _validate_email(email: str) -> None:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Raises:
            UserValidationException: If email format is invalid
        """
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email.strip()):
            raise UserValidationException(
                "email",
                "Invalid email format. Must be in format: user@example.com",
                value=email,
            )

    @staticmethod
    def _validate_raw_password(raw_password: str) -> None:
        """
        Validate password strength.

        Args:
            raw_password: Password to validate

        Raises:
            UserValidationException: If password doesn't meet strength requirements
        """
        if len(raw_password) < 8:
            raise UserValidationException(
                "password",
                "Password must be at least 8 characters long",
                value="[REDACTED]",
            )
        if not any(char.isdigit() for char in raw_password):
            raise UserValidationException(
                "password",
                "Password must contain at least one digit",
                value="[REDACTED]",
            )
        if not any(char.isupper() for char in raw_password):
            raise UserValidationException(
                "password",
                "Password must contain at least one uppercase letter",
                value="[REDACTED]",
            )
        if not any(char.islower() for char in raw_password):
            raise UserValidationException(
                "password",
                "Password must contain at least one lowercase letter",
                value="[REDACTED]",
            )
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?" for char in raw_password):
            raise UserValidationException(
                "password",
                "Password must contain at least one special character",
                value="[REDACTED]",
            )

    @staticmethod
    def _validate_phone_number(phone_number: str) -> None:
        """
        Validate phone number format.

        Args:
            phone_number: Phone number to validate

        Raises:
            UserValidationException: If phone number format is invalid
        """
        cleaned_phone = phone_number.replace(" ", "").replace("-", "")

        phone_pattern = r"^\+\d{10,15}$"
        if not re.match(phone_pattern, cleaned_phone):
            raise UserValidationException(
                "phone_number",
                "Phone number must be in international format: +[country code][number] (10-15 digits)",
                value=phone_number,
            )

    @staticmethod
    def _validate_full_name(first_name: str, last_name: str) -> None:
        """
        Validate first and last names.

        Args:
            first_name: First name to validate
            last_name: Last name to validate

        Raises:
            UserValidationException: If name validation fails
        """
        name_pattern = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$"

        if not re.match(name_pattern, first_name):
            raise UserValidationException(
                "first_name",
                "First name must contain only alphabetic characters, spaces, hyphens, or apostrophes",
                value=first_name,
            )

        if not re.match(name_pattern, last_name):
            raise UserValidationException(
                "last_name",
                "Last name must contain only alphabetic characters, spaces, hyphens, or apostrophes",
                value=last_name,
            )

        if len(first_name) < 2 or len(first_name) > 50:
            raise UserValidationException(
                "first_name",
                "First name must be between 2 and 50 characters long",
                value=first_name,
            )

        if len(last_name) < 2 or len(last_name) > 50:
            raise UserValidationException(
                "last_name",
                "Last name must be between 2 and 50 characters long",
                value=last_name,
            )

    def __repr__(self) -> str:
        """Return string representation of the user."""
        return (
            f"User(id={self._user_id}, email='{self._email}', "
            f"name='{self.full_name}', roles={[r.value for r in self._roles]}, "
            f"active={self._is_active})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on user_id or email."""
        if not isinstance(other, User):
            return False

        if self._user_id is not None and other._user_id is not None:
            return self._user_id == other._user_id

        return self._email == other._email

    def __hash__(self) -> int:
        """Return hash based on user_id or email."""
        return hash(self._user_id if self._user_id else self._email)
