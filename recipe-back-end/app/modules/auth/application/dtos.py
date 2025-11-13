from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import List, Optional
from datetime import datetime
from app.modules.auth.domain.user import User, UserRecipeStats


class SignUpRequest(BaseModel):
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: EmailStr = Field(..., description="User's email address")
    gender: str = Field(..., description="User's gender")
    date_of_birth: datetime = Field(..., description="User's date of birth")
    password: str = Field(..., description="User's password")
    phone_number: Optional[str] = Field(None, description="User's phone number")

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if len(v.strip()) < 2 or len(v.strip()) > 50:
            raise ValueError("Name must be between 2 and 50 characters")
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 70:
            raise ValueError(
                "Password must be at least 8 and at most 70 characters long"
            )
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None:
            digits = "".join(filter(str.isdigit, v))
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        allowed_genders = {
            "male",
            "female",
            "other",
        }
        if v.lower() not in allowed_genders:
            raise ValueError(f"Gender must be one of {allowed_genders}")
        return v.lower()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v):
        if v is not None:
            if v >= datetime.now():
                raise ValueError("Date of birth must be in the past")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class UserProfileResponse(BaseModel):
    id: str = Field(..., alias="user_id")
    # Personal information
    full_name: str = Field(..., description="Full name of the user")
    profile_picture_url: Optional[str] = Field(
        None, description="URL of the user's profile picture"
    )
    bio: Optional[str] = Field(None, description="Short biography of the user")
    date_of_birth: Optional[datetime] = Field(
        None, description="Date of birth of the user"
    )
    gender: Optional[str] = Field(None, description="Gender of the user")

    # Contact information
    email: str = Field(..., description="User's email address")
    phone_number: Optional[str] = Field(None, description="User's phone number")

    # Status information
    joined_at: datetime = Field(..., description="Date and time the user joined")
    last_login: Optional[datetime] = Field(
        None, description="Date and time of the user's last login"
    )

    # User Stats
    favorite_recipes_count: int = Field(..., description="Number of favorite recipes")
    created_recipes_count: int = Field(..., description="Number of created recipes")
    reviewed_recipes_count: int = Field(..., description="Number of reviewed recipes")

    @classmethod
    def from_user_and_stats(
        cls, user: User, stats: UserRecipeStats
    ) -> "UserProfileResponse":
        return cls(
            user_id=str(user.id),
            full_name=f"{user.first_name} {user.last_name}",
            profile_picture_url=user.profile_picture_url,
            bio=user.bio,
            date_of_birth=user.date_of_birth,
            gender=user.gender.value if user.gender else None,
            email=user.email,
            phone_number=user.phone_number,
            joined_at=user.joined_at,
            last_login=user.last_login,
            favorite_recipes_count=stats.favorite_recipes_count,
            created_recipes_count=stats.created_recipes_count,
            reviewed_recipes_count=stats.reviewed_recipes_count,
        )


class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    roles: List[str]
    is_active: bool
    joined_at: datetime
    last_login: Optional[datetime]


class UpdateUserProfileRequest(BaseModel):
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    gender: Optional[str] = Field("unknown", description="User's gender")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    bio: Optional[str] = Field(None, description="Short biography of the user")
    profile_picture_url: Optional[str] = Field(
        None, description="URL of the user's profile picture"
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Name cannot be empty")
            if len(v.strip()) < 2 or len(v.strip()) > 50:
                raise ValueError("Name must be between 2 and 50 characters")
            if not v.replace(" ", "").isalpha():
                raise ValueError("Name must contain only alphabetic characters")
            return v.strip()
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None:
            digits = "".join(filter(str.isdigit, v))
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None:
            allowed_genders = {"male", "female", "non-binary", "other", "unknown"}
            if v.lower() not in allowed_genders:
                raise ValueError(f"Gender must be one of {allowed_genders}")
            return v.lower()
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v):
        if v is not None:
            if v >= datetime.now():
                raise ValueError("Date of birth must be in the past")
        return v
