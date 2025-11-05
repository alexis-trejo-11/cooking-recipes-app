import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add the parent directory to Python path BEFORE importing app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.auth.domain.user import User, UserRole, UserId
from app.auth.domain.exceptions import (
    UserValidationException,
    UserCreationException,
    UserReconstructionException,
    UserUpdateException,
    UserSecurityException,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Provide sample valid user data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "raw_password": "SecurePass123!",
        "phone_number": "+1234567890",
        "roles": [UserRole.PREMIUM_USER],
    }


@pytest.fixture
def sample_persisted_user_data() -> Dict[str, Any]:
    """Provide sample persisted user data for reconstruction testing."""
    return {
        "user_id": UserId(1),
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "password": "hashed_password_123",
        "phone_number": "+1987654321",
        "roles": [UserRole.ADMIN.value, UserRole.MODERATOR.value],
        "joined_at": "2024-01-01T10:00:00+00:00",
        "last_login": "2024-01-15T14:30:00+00:00",
        "is_active": True,
    }


@pytest.fixture
def mock_db_session():
    """Provide a mock database session."""
    return AsyncMock()
