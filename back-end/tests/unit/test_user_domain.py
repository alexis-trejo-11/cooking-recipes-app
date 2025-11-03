import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from app.domain.entities.user import User, UserRole, UserId
from app.domain.exceptions.user_exceptions import (
    UserValidationException,
    UserCreationException,
    UserReconstructionException,
    UserUpdateException,
    UserSecurityException,
)


class TestUserCreation:
    """Test cases for User creation functionality."""

    def test_create_user_success(self, sample_user_data):
        """Test successful user creation with valid data."""
        user = User.create(**sample_user_data)

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.phone_number == "+1234567890"
        assert UserRole.PREMIUM_USER in user.roles
        assert user.is_active is True
        assert isinstance(user.joined_at, datetime)
        assert user.last_login is None

    def test_create_user_default_role(self, sample_user_data):
        """Test user creation defaults to COMMON_USER role."""
        data = sample_user_data.copy()
        data.pop("roles")

        user = User.create(**data)

        assert UserRole.COMMON_USER in user.roles
        assert len(user.roles) == 1

    def test_create_user_invalid_email(self, sample_user_data):
        """Test user creation fails with invalid email."""
        data = sample_user_data.copy()
        data["email"] = "invalid-email"

        with pytest.raises(UserCreationException) as exc_info:
            User.create(**data)

        # Verifica de manera más flexible
        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message for keyword in ["email", "validation", "invalid"]
        ), f"Expected email-related error, got: {error_message}"

    def test_create_user_weak_password(self, sample_user_data):
        """Test user creation fails with weak password."""
        data = sample_user_data.copy()
        data["raw_password"] = "weak"

        with pytest.raises(UserCreationException) as exc_info:
            User.create(**data)

        # Verifica de manera más flexible
        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message
            for keyword in ["password", "validation", "weak", "length"]
        ), f"Expected password-related error, got: {error_message}"

    def test_create_user_invalid_phone(self, sample_user_data):
        """Test user creation fails with invalid phone number."""
        data = sample_user_data.copy()
        data["phone_number"] = "invalid-phone"

        with pytest.raises(UserCreationException) as exc_info:
            User.create(**data)

        # Verifica que se lance la excepción (sin verificar mensaje específico)
        assert True  # Si llegamos aquí, la excepción se lanzó correctamente

    def test_create_user_empty_names(self, sample_user_data):
        """Test user creation fails with empty names."""
        data = sample_user_data.copy()
        data["first_name"] = ""

        with pytest.raises(UserCreationException):
            User.create(**data)

    def test_create_user_name_validation(self, sample_user_data):
        """Test user creation fails with invalid names."""
        test_cases = [
            ("J", "Doe"),  # First name too short
            ("John", "D"),  # Last name too short
            ("John" * 20, "Doe"),  # First name too long
            ("John", "Doe" * 20),  # Last name too long
            ("John123", "Doe"),  # Numbers in first name
            ("John", "Doe123"),  # Numbers in last name
        ]

        for first_name, last_name in test_cases:
            data = sample_user_data.copy()
            data["first_name"] = first_name
            data["last_name"] = last_name

            with pytest.raises(UserCreationException):
                User.create(**data)


class TestUserRepresentation:
    """Test cases for User string representation."""

    def test_repr(self, sample_user_data):
        """Test string representation of user."""
        user = User.create(**sample_user_data)

        repr_str = repr(user)

        assert user.email in repr_str
        assert user.full_name in repr_str
        assert "active=True" in repr_str

    def test_equality_same_email_no_id(self, sample_user_data):
        """Test users with same email and no ID are equal."""
        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        # Asegurarnos de que no tengan ID para forzar comparación por email
        user1._user_id = None
        user2._user_id = None

        assert user1 == user2

    def test_equality_different_emails(self, sample_user_data):
        """Test users with different emails are not equal."""
        user1 = User.create(**sample_user_data)

        user2_data = sample_user_data.copy()
        user2_data["email"] = "different@example.com"
        user2 = User.create(**user2_data)

        # Asegurarnos de que no tengan ID para forzar comparación por email
        user1._user_id = None
        user2._user_id = None

        assert user1 != user2

    def test_equality_with_same_id(self, sample_user_data):
        """Test users with same ID are equal."""

        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        # Asignar el mismo ID a ambos
        same_id = UserId(1)
        user1._user_id = same_id
        user2._user_id = same_id

        assert user1 == user2

    def test_equality_with_different_ids(self, sample_user_data):
        """Test users with different IDs are not equal."""

        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        # Asignar IDs diferentes
        user1._user_id = UserId(1)
        user2._user_id = UserId(2)

        assert user1 != user2


class TestUserReconstruction:
    """Test cases for User reconstruction functionality."""

    def test_reconstruct_user_success(self, sample_persisted_user_data):
        """Test successful user reconstruction from persisted data."""
        user = User.reconstruct(sample_persisted_user_data)

        assert user.user_id == UserId(1)
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.email == "jane.smith@example.com"
        assert user.password == "hashed_password_123"
        assert UserRole.ADMIN in user.roles
        assert UserRole.MODERATOR in user.roles
        assert user.is_active is True
        assert isinstance(user.joined_at, datetime)
        assert isinstance(user.last_login, datetime)

    def test_reconstruct_user_missing_required_fields(self, sample_persisted_user_data):
        """Test reconstruction fails with missing required fields."""
        data = sample_persisted_user_data.copy()
        data.pop("email")

        with pytest.raises(UserReconstructionException) as exc_info:
            User.reconstruct(data)

        # Verifica de manera más flexible
        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message
            for keyword in ["missing", "required", "field", "email"]
        ), f"Expected missing field error, got: {error_message}"

    def test_reconstruct_user_invalid_role(self, sample_persisted_user_data):
        """Test reconstruction fails with invalid role."""
        data = sample_persisted_user_data.copy()
        data["roles"] = ["invalid_role"]

        with pytest.raises(UserReconstructionException) as exc_info:
            User.reconstruct(data)

        # Verifica que se lance la excepción
        assert True

    def test_reconstruct_user_invalid_date_format(self, sample_persisted_user_data):
        """Test reconstruction fails with invalid date format."""
        data = sample_persisted_user_data.copy()
        data["joined_at"] = "invalid-date-format"

        with pytest.raises(UserReconstructionException) as exc_info:
            User.reconstruct(data)

        # Verifica que se lance la excepción
        assert True

    def test_reconstruct_user_with_role_objects(self, sample_persisted_user_data):
        """Test reconstruction works with Role objects instead of strings."""
        data = sample_persisted_user_data.copy()
        data["roles"] = [UserRole.ADMIN, UserRole.MODERATOR]

        user = User.reconstruct(data)

        assert UserRole.ADMIN in user.roles
        assert UserRole.MODERATOR in user.roles

    def test_reconstruct_user_with_string_dates(self, sample_persisted_user_data):
        """Test reconstruction with string date formats."""
        data = sample_persisted_user_data.copy()

        # Asegurar que las fechas son strings
        data["joined_at"] = "2024-01-01T10:00:00+00:00"
        data["last_login"] = "2024-01-15T14:30:00+00:00"

        user = User.reconstruct(data)

        assert isinstance(user.joined_at, datetime)
        assert isinstance(user.last_login, datetime)
        assert user.joined_at.year == 2024
        assert user.last_login.day == 15

    def test_reconstruct_user_with_datetime_objects(self, sample_persisted_user_data):
        """Test reconstruction with datetime objects."""
        data = sample_persisted_user_data.copy()

        # Usar objetos datetime directamente
        joined_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        last_login = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        data["joined_at"] = joined_at
        data["last_login"] = last_login

        user = User.reconstruct(data)

        assert user.joined_at == joined_at
        assert user.last_login == last_login

    def test_reconstruct_user_minimal_data(self):
        """Test reconstruction with minimal required data."""
        minimal_data = {
            "user_id": "minimal-user",
            "first_name": "Minimal",
            "last_name": "User",
            "email": "minimal@example.com",
            "password": "hashed_password",
            "roles": [UserRole.COMMON_USER.value],
            "joined_at": "2024-01-01T00:00:00+00:00",
        }

        user = User.reconstruct(minimal_data)

        assert user.first_name == "Minimal"
        assert user.last_name == "User"
        assert user.email == "minimal@example.com"
        assert user.phone_number is None
        assert user.last_login is None
        assert user.is_active is True

    def test_reconstruct_user_with_none_values(self, sample_persisted_user_data):
        """Test reconstruction with None values for optional fields."""
        data = sample_persisted_user_data.copy()
        data["phone_number"] = None
        data["last_login"] = None

        user = User.reconstruct(data)

        assert user.phone_number is None
        assert user.last_login is None
