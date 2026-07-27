from datetime import datetime

import pytest

from app.modules.auth.application.auth_use_cases import SignUpUseCase, LoginUseCase
from app.modules.auth.application.dtos import SignUpRequest, LoginRequest
from app.modules.auth.infrastucture.mocks.mock_repositories import (
    MockUserRepository,
    MockSessionRepository,
)
from app.modules.auth.infrastucture.mocks.mock_services import (
    MockPasswordHasher,
    MockTokenService,
)
from app.modules.auth.application.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)


ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


class TestAuthUseCases:
    @pytest.fixture
    def dependencies(self):
        repo = MockUserRepository()
        hasher = MockPasswordHasher()
        token_service = MockTokenService()
        session_repo = MockSessionRepository()
        return repo, hasher, token_service, session_repo

    @pytest.fixture
    def signup_request(self):
        return SignUpRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            gender="male",
            date_of_birth=datetime(1990, 5, 15),
            password="SecurePass123!",
            phone_number="+1234567890",
        )

    def _signup_use_case(self, dependencies):
        repo, hasher, token_service, session_repo = dependencies
        return SignUpUseCase(
            repo,
            hasher,
            token_service,
            session_repo,
            refresh_token_expire_days=REFRESH_TOKEN_EXPIRE_DAYS,
            access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    def _login_use_case(self, dependencies):
        repo, hasher, token_service, session_repo = dependencies
        return LoginUseCase(
            repo,
            hasher,
            token_service,
            session_repo,
            REFRESH_TOKEN_EXPIRE_DAYS,
            ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    @pytest.mark.asyncio
    async def test_signup_success(self, dependencies, signup_request):
        _, _, token_service, session_repo = dependencies
        use_case = self._signup_use_case(dependencies)

        result = await use_case.execute(signup_request)

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"
        assert result.expires_in == ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert result.user_id
        assert result.user_id != "0"

        payload = await token_service.verify_access_token(result.access_token)
        assert payload["email"] == signup_request.email
        assert payload["sub"] == result.user_id

        sessions = list(session_repo._sessions.values())
        assert len(sessions) == 1
        assert sessions[0].user_id == result.user_id

    @pytest.mark.asyncio
    async def test_signup_user_already_exists(self, dependencies, signup_request):
        use_case = self._signup_use_case(dependencies)

        await use_case.execute(signup_request)

        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(signup_request)

    @pytest.mark.asyncio
    async def test_login_success(self, dependencies, signup_request):
        await self._signup_use_case(dependencies).execute(signup_request)

        login_request = LoginRequest(
            email=signup_request.email, password=signup_request.password
        )
        result = await self._login_use_case(dependencies).execute(login_request)

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"
        assert result.user_id

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, dependencies):
        use_case = self._login_use_case(dependencies)

        login_request = LoginRequest(
            email="nonexistent@example.com", password="WrongPass123!"
        )

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(login_request)
