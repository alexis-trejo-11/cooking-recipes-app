from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    first_name: str
    last_name: str
    roles: list[str]


class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    roles: list[str]
    is_active: bool
    joined_at: datetime
    last_login: Optional[datetime]


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2 or len(v.strip()) > 50:
                raise ValueError("Name must be between 2 and 50 characters")
            if not v.replace(" ", "").isalpha():
                raise ValueError("Name must contain only alphabetic characters")
        return v.strip() if v else v
