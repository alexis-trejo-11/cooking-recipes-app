import pytest
import jwt
from app.modules.auth.application.auth_use_cases import SignUpUseCase, LoginUseCase
from app.modules.auth.application.dtos import SignUpRequest, LoginRequest
from app.modules.auth.infrastucture.mocks.mock_repositories import MockUserRepository
from app.modules.auth.infrastucture.mocks.mock_services import (
    MockPasswordHasher,
    MockTokenService,
)
from app.modules.auth.application.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)


class TestAuthUseCases:
    @pytest.fixture
    def dependencies(self):
        repo = MockUserRepository()
        hasher = MockPasswordHasher()
        token_service = MockTokenService()
        return repo, hasher, token_service

    @pytest.fixture
    def signup_request(self):
        return SignUpRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="SecurePass123!",
            phone_number="+1234567890",
        )

    @pytest.mark.asyncio
    async def test_signup_success(self, dependencies, signup_request):
        repo, hasher, token_service = dependencies
        use_case = SignUpUseCase(repo, hasher, token_service)

        result = await use_case.execute(signup_request)

        assert result.email == signup_request.email
        assert result.first_name == signup_request.first_name
        assert result.last_name == signup_request.last_name
        assert "common_user" in result.roles
        assert result.access_token is not None

        # Verify token can be decoded
        payload = await token_service.verify_access_token(result.access_token)
        assert payload["email"] == signup_request.email

    @pytest.mark.asyncio
    async def test_signup_user_already_exists(self, dependencies, signup_request):
        repo, hasher, token_service = dependencies
        use_case = SignUpUseCase(repo, hasher, token_service)

        await use_case.execute(signup_request)

        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(signup_request)

    @pytest.mark.asyncio
    async def test_login_success(self, dependencies, signup_request):
        repo, hasher, token_service = dependencies
        signup_use_case = SignUpUseCase(repo, hasher, token_service)
        login_use_case = LoginUseCase(repo, hasher, token_service)

        await signup_use_case.execute(signup_request)

        login_request = LoginRequest(
            email=signup_request.email, password=signup_request.password
        )

        result = await login_use_case.execute(login_request)

        assert result.email == signup_request.email
        assert result.access_token is not None

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, dependencies):
        repo, hasher, token_service = dependencies
        use_case = LoginUseCase(repo, hasher, token_service)

        login_request = LoginRequest(
            email="nonexistent@example.com", password="wrongpassword"
        )

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(login_request)
