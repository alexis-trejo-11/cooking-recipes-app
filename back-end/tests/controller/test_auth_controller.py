import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from app.auth.presentation import auth_controller
from app.auth.application.auth_use_cases import SignUpUseCase, LoginUseCase
from app.auth.application.dtos import SignUpRequest, LoginRequest, AuthResponse
from app.auth.application.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)


class TestAuthController:
    """Test cases for Auth Controller"""

    @pytest.fixture
    def mock_signup_use_case(self):
        """Mock SignUpUseCase"""
        return AsyncMock(spec=SignUpUseCase)

    @pytest.fixture
    def mock_login_use_case(self):
        """Mock LoginUseCase"""
        return AsyncMock(spec=LoginUseCase)

    @pytest.fixture
    def signup_request(self):
        """Sample signup request"""
        return SignUpRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="SecurePass123!",
            phone_number="+1234567890",
        )

    @pytest.fixture
    def login_request(self):
        """Sample login request"""
        return LoginRequest(email="john.doe@example.com", password="SecurePass123!")

    @pytest.fixture
    def auth_response(self):
        """Sample auth response"""
        return AuthResponse(
            access_token="test_token_123",
            token_type="bearer",
            user_id="1",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            roles=["common_user"],
        )

    @pytest.mark.asyncio
    async def test_signup_success(
        self, mock_signup_use_case, signup_request, auth_response
    ):
        """Test successful user signup"""
        # Setup
        mock_signup_use_case.execute.return_value = auth_response

        # Execute
        result = await auth_controller.signup(
            request=signup_request, use_case=mock_signup_use_case
        )

        # Assert
        mock_signup_use_case.execute.assert_called_once_with(signup_request)
        assert result == auth_response
        assert result.access_token == "test_token_123"
        assert result.email == "john.doe@example.com"

    @pytest.mark.asyncio
    async def test_signup_user_already_exists(
        self, mock_signup_use_case, signup_request
    ):
        """Test signup when user already exists"""
        # Setup
        mock_signup_use_case.execute.side_effect = UserAlreadyExistsException(
            "User with email john.doe@example.com already exists"
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.signup(
                request=signup_request, use_case=mock_signup_use_case
            )

        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_signup_validation_error(self, mock_signup_use_case, signup_request):
        """Test signup with validation error"""
        # Setup
        mock_signup_use_case.execute.side_effect = ValueError("Invalid email format")

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.signup(
                request=signup_request, use_case=mock_signup_use_case
            )

        assert exc_info.value.status_code == 422
        assert "Invalid email format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_success(
        self, mock_login_use_case, login_request, auth_response
    ):
        """Test successful user login"""
        # Setup
        mock_login_use_case.execute.return_value = auth_response

        # Execute
        result = await auth_controller.login(
            request=login_request, use_case=mock_login_use_case
        )

        # Assert
        mock_login_use_case.execute.assert_called_once_with(login_request)
        assert result == auth_response
        assert result.access_token == "test_token_123"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_login_use_case, login_request):
        """Test login with invalid credentials"""
        # Setup
        mock_login_use_case.execute.side_effect = InvalidCredentialsException(
            "Invalid email or password"
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.login(
                request=login_request, use_case=mock_login_use_case
            )

        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_login_use_case, login_request):
        """Test login when user doesn't exist"""
        # Setup
        mock_login_use_case.execute.side_effect = InvalidCredentialsException(
            "User not found"
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.login(
                request=login_request, use_case=mock_login_use_case
            )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_signup_unexpected_error(self, mock_signup_use_case, signup_request):
        """Test signup with unexpected error"""
        # Setup
        mock_signup_use_case.execute.side_effect = Exception(
            "Database connection failed"
        )

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await auth_controller.signup(
                request=signup_request, use_case=mock_signup_use_case
            )

        assert exc_info.value.status_code == 500
        assert "An unexpected error occurred during registration" in str(
            exc_info.value.detail
        )


# Tests de Integración con TestClient
class TestAuthControllerIntegration:
    """Integration tests for Auth Controller with TestClient"""

    @pytest.fixture
    def client(self, mock_dependencies):
        """Create TestClient with mocked dependencies"""
        from fastapi.testclient import TestClient
        import main
        from app.auth.presentation.depencies import (
            get_signup_use_case,
            get_login_use_case,
        )

        # Override dependencies
        main.app.dependency_overrides[get_signup_use_case] = lambda: mock_dependencies[
            "signup_use_case"
        ]
        main.app.dependency_overrides[get_login_use_case] = lambda: mock_dependencies[
            "login_use_case"
        ]

        client = TestClient(main.app)
        yield client

        # Clear overrides after test
        main.app.dependency_overrides.clear()

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies for integration tests"""
        # Mock the use cases
        mock_signup_use_case = AsyncMock(spec=SignUpUseCase)
        mock_login_use_case = AsyncMock(spec=LoginUseCase)

        return {
            "signup_use_case": mock_signup_use_case,
            "login_use_case": mock_login_use_case,
        }

    def test_signup_endpoint_success(self, client, mock_dependencies):
        """Test signup endpoint success"""
        # Setup
        auth_response = AuthResponse(
            access_token="test_token_123",
            token_type="bearer",
            user_id="1",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            roles=["common_user"],
        )
        mock_dependencies["signup_use_case"].execute.return_value = auth_response

        # Execute
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "phone_number": "+1234567890",
            },
        )

        # Assert
        assert response.status_code == 201  # Created
        data = response.json()
        assert data["access_token"] == "test_token_123"
        assert data["email"] == "john.doe@example.com"

    def test_signup_endpoint_validation_error(self, client, mock_dependencies):
        """Test signup endpoint with validation error from use case"""
        # Setup - Use case raises ValueError after Pydantic validation passes
        mock_dependencies["signup_use_case"].execute.side_effect = ValueError(
            "Invalid email format"
        )

        # Execute - Send valid data that passes Pydantic validation
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",  # Valid email format
                "password": "ValidPass123!",  # Valid password
            },
        )

        # Assert - Should return 422 with the ValueError message
        assert response.status_code == 422  # Unprocessable Entity
        assert "Invalid email format" in response.json()["detail"]

    def test_login_endpoint_success(self, client, mock_dependencies):
        """Test login endpoint success"""
        # Setup
        auth_response = AuthResponse(
            access_token="test_token_123",
            token_type="bearer",
            user_id="1",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            roles=["common_user"],
        )
        mock_dependencies["login_use_case"].execute.return_value = auth_response

        # Execute
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "john.doe@example.com", "password": "SecurePass123!"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_token_123"

    def test_login_endpoint_invalid_credentials(self, client, mock_dependencies):
        """Test login endpoint with invalid credentials"""
        # Setup
        mock_dependencies["login_use_case"].execute.side_effect = (
            InvalidCredentialsException("Invalid email or password")
        )

        # Execute
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "john.doe@example.com", "password": "wrongpassword"},
        )

        # Assert
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
