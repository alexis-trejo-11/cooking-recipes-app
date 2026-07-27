import pytest
from datetime import datetime, timezone

from app.modules.auth.domain.user import User, UserRole, UserId, UserGender
from app.modules.auth.domain.exceptions import (
    UserCreationException,
    UserReconstructionException,
)


class TestUserCreation:
    """Test cases for User creation functionality."""

    def test_create_user_success(self, sample_user_data):
        user = User.create(**sample_user_data)

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.phone_number == "+1234567890"
        assert user.gender == UserGender.MALE
        assert UserRole.PREMIUM_USER in user.roles
        assert user.is_active is True
        assert isinstance(user.joined_at, datetime)
        assert user.last_login is None

    def test_create_user_default_role(self, sample_user_data):
        data = sample_user_data.copy()
        data.pop("roles")

        user = User.create(**data)

        assert UserRole.COMMON_USER in user.roles
        assert len(user.roles) == 1

    def test_create_user_invalid_email(self, sample_user_data):
        data = sample_user_data.copy()
        data["email"] = "invalid-email"

        with pytest.raises(UserCreationException) as exc_info:
            User.create(**data)

        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message for keyword in ["email", "validation", "invalid"]
        ), f"Expected email-related error, got: {error_message}"

    def test_create_user_weak_password(self, sample_user_data):
        data = sample_user_data.copy()
        data["raw_password"] = "weak"

        with pytest.raises(UserCreationException) as exc_info:
            User.create(**data)

        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message
            for keyword in ["password", "validation", "weak", "length"]
        ), f"Expected password-related error, got: {error_message}"

    def test_create_user_invalid_phone(self, sample_user_data):
        data = sample_user_data.copy()
        data["phone_number"] = "invalid-phone"

        with pytest.raises(UserCreationException):
            User.create(**data)

    def test_create_user_empty_names(self, sample_user_data):
        data = sample_user_data.copy()
        data["first_name"] = ""

        with pytest.raises(UserCreationException):
            User.create(**data)

    def test_create_user_name_validation(self, sample_user_data):
        test_cases = [
            ("J", "Doe"),
            ("John", "D"),
            ("John" * 20, "Doe"),
            ("John", "Doe" * 20),
            ("John123", "Doe"),
            ("John", "Doe123"),
        ]

        for first_name, last_name in test_cases:
            data = sample_user_data.copy()
            data["first_name"] = first_name
            data["last_name"] = last_name

            with pytest.raises(UserCreationException):
                User.create(**data)

    def test_create_user_future_date_of_birth_fails(self, sample_user_data):
        data = sample_user_data.copy()
        data["date_of_birth"] = datetime.now(timezone.utc).replace(year=2099)

        with pytest.raises(UserCreationException):
            User.create(**data)


class TestUserRepresentation:
    """Test cases for User string representation and equality."""

    def test_repr(self, sample_user_data):
        user = User.create(**sample_user_data)

        repr_str = repr(user)

        assert user.email in repr_str
        assert user.full_name in repr_str
        assert "active=True" in repr_str

    def test_equality_same_email_no_id(self, sample_user_data):
        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        user1._user_id = None
        user2._user_id = None

        assert user1 == user2

    def test_equality_different_emails(self, sample_user_data):
        user1 = User.create(**sample_user_data)

        user2_data = sample_user_data.copy()
        user2_data["email"] = "different@example.com"
        user2 = User.create(**user2_data)

        user1._user_id = None
        user2._user_id = None

        assert user1 != user2

    def test_equality_with_same_id(self, sample_user_data):
        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        same_id = UserId(1)
        user1._user_id = same_id
        user2._user_id = same_id

        assert user1 == user2

    def test_equality_with_different_ids(self, sample_user_data):
        user1 = User.create(**sample_user_data)
        user2 = User.create(**sample_user_data)

        user1._user_id = UserId(1)
        user2._user_id = UserId(2)

        assert user1 != user2


class TestUserReconstruction:
    """Test cases for User reconstruction functionality."""

    def test_reconstruct_user_success(self, sample_persisted_user_data):
        user = User.reconstruct(sample_persisted_user_data)

        assert user.id == UserId(1)
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.email == "jane.smith@example.com"
        assert user.password == "hashed_password_123"
        assert user.gender == UserGender.FEMALE
        assert UserRole.ADMIN in user.roles
        assert UserRole.MODERATOR in user.roles
        assert user.is_active is True
        assert isinstance(user.joined_at, datetime)
        assert isinstance(user.last_login, datetime)

    def test_reconstruct_user_missing_required_fields(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data.pop("email")

        with pytest.raises(UserReconstructionException) as exc_info:
            User.reconstruct(data)

        error_message = str(exc_info.value).lower()
        assert any(
            keyword in error_message
            for keyword in ["missing", "required", "field", "email"]
        ), f"Expected missing field error, got: {error_message}"

    def test_reconstruct_user_invalid_role(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data["roles"] = ["invalid_role"]

        with pytest.raises(UserReconstructionException):
            User.reconstruct(data)

    def test_reconstruct_user_invalid_date_format(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data["joined_at"] = "invalid-date-format"

        with pytest.raises(UserReconstructionException):
            User.reconstruct(data)

    def test_reconstruct_user_with_role_objects(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data["roles"] = [UserRole.ADMIN, UserRole.MODERATOR]

        user = User.reconstruct(data)

        assert UserRole.ADMIN in user.roles
        assert UserRole.MODERATOR in user.roles

    def test_reconstruct_user_with_string_dates(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data["joined_at"] = "2024-01-01T10:00:00+00:00"
        data["last_login"] = "2024-01-15T14:30:00+00:00"

        user = User.reconstruct(data)

        assert isinstance(user.joined_at, datetime)
        assert isinstance(user.last_login, datetime)
        assert user.joined_at.year == 2024
        assert user.last_login.day == 15

    def test_reconstruct_user_with_datetime_objects(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        joined_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        last_login = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        data["joined_at"] = joined_at
        data["last_login"] = last_login

        user = User.reconstruct(data)

        assert user.joined_at == joined_at
        assert user.last_login == last_login

    def test_reconstruct_user_minimal_data(self):
        minimal_data = {
            "id": UserId(42),
            "first_name": "Minimal",
            "last_name": "User",
            "email": "minimal@example.com",
            "password": "hashed_password",
            "roles": [UserRole.COMMON_USER.value],
            "joined_at": "2024-01-01T00:00:00+00:00",
            "gender": UserGender.OTHER,
            "is_active": True,
            "date_of_birth": None,
            "profile_picture_url": None,
            "bio": "",
        }

        user = User.reconstruct(minimal_data)

        assert user.id == UserId(42)
        assert user.first_name == "Minimal"
        assert user.last_name == "User"
        assert user.email == "minimal@example.com"
        assert user.gender == UserGender.OTHER
        assert user.phone_number is None
        assert user.last_login is None
        assert user.is_active is True

    def test_reconstruct_user_with_none_values(self, sample_persisted_user_data):
        data = sample_persisted_user_data.copy()
        data["phone_number"] = None
        data["last_login"] = None
        data["date_of_birth"] = None

        user = User.reconstruct(data)

        assert user.phone_number is None
        assert user.last_login is None
        assert user.date_of_birth is None
