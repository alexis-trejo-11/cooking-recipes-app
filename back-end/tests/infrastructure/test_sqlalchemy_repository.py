from app.modules.auth.infrastucture.persitence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.modules.auth.domain.user import User, UserRole, UserId
from config.sql_session import Base


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create async session for testing"""
    # Create in-memory SQLite database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.fixture
def sample_user():
    """Create sample user for testing"""
    return User.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        raw_password="SecurePass123!",
        roles=[UserRole.COMMON_USER],
    )


class TestSQLAlchemyUserRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_user(self, db_session, sample_user):
        """Test saving and retrieving user"""
        repository = SQLAlchemyUserRepository(db_session)

        # Save user
        saved_user = await repository.save(sample_user)

        # Retrieve user
        retrieved_user = await repository.get_by_id(saved_user.user_id)

        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.first_name == sample_user.first_name
        assert retrieved_user.user_id.value == saved_user.user_id.value

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session, sample_user):
        """Test getting user by email"""
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)

        retrieved_user = await repository.get_by_email(saved_user.email)

        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.first_name == sample_user.first_name

    @pytest.mark.asyncio
    async def test_exists_by_email(self, db_session, sample_user):
        """Test checking if user exists by email"""
        repository = SQLAlchemyUserRepository(db_session)

        # Should not exist before saving
        exists = await repository.exists_by_email(sample_user.email)
        assert exists is False

        # Save user
        await repository.save(sample_user)

        # Should exist after saving
        exists = await repository.exists_by_email(sample_user.email)
        assert exists is True

        # Check non-existent email
        exists = await repository.exists_by_email("nonexistent@example.com")
        assert exists is False

    @pytest.mark.asyncio
    async def test_update_user(self, db_session, sample_user):
        """Test updating user"""
        repository = SQLAlchemyUserRepository(db_session)

        # Save initial user
        saved_user = await repository.save(sample_user)

        # Update user
        saved_user.update_names("Jane", "Smith")
        saved_user.update_email("jane.smith@example.com")

        updated_user = await repository.save(saved_user)

        # Retrieve and verify
        retrieved_user = await repository.get_by_id(saved_user.user_id)

        assert retrieved_user.first_name == "Jane"
        assert retrieved_user.last_name == "Smith"
        assert retrieved_user.email == "jane.smith@example.com"

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session, sample_user):
        """Test deleting user"""
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)

        # Verify user exists
        user_exists = await repository.exists_by_email(saved_user.email)
        assert user_exists is True

        # Delete user
        deleted = await repository.delete(saved_user.user_id)
        assert deleted is True

        # Verify user is gone
        retrieved_user = await repository.get_by_id(saved_user.user_id)
        assert retrieved_user is None

        exists = await repository.exists_by_email(saved_user.email)
        assert exists is False

    @pytest.mark.asyncio
    async def test_list_users(self, db_session, sample_user):
        """Test listing users"""
        repository = SQLAlchemyUserRepository(db_session)

        # Should be empty initially
        users = await repository.list_all()
        assert len(users) == 0

        # Save multiple users
        user1 = await repository.save(sample_user)

        user2_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "raw_password": "SecurePass123!",
            "roles": [UserRole.PREMIUM_USER],
        }
        user2 = User.create(**user2_data)
        await repository.save(user2)

        # List users
        users = await repository.list_all()

        assert len(users) == 2
        emails = [user.email for user in users]
        assert "john.doe@example.com" in emails
        assert "jane.smith@example.com" in emails

    @pytest.mark.asyncio
    async def test_user_roles_persistence(self, db_session):
        """Test that user roles are properly persisted and retrieved"""
        repository = SQLAlchemyUserRepository(db_session)

        user = User.create(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            raw_password="SecurePass123!",
            roles=[UserRole.ADMIN, UserRole.MODERATOR],
        )

        saved_user = await repository.save(user)
        retrieved_user = await repository.get_by_id(saved_user.user_id)

        assert UserRole.ADMIN in retrieved_user.roles
        assert UserRole.MODERATOR in retrieved_user.roles
        assert len(retrieved_user.roles) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db_session):
        """Test getting user that doesn't exist"""
        repository = SQLAlchemyUserRepository(db_session)

        user = await repository.get_by_id(UserId(999))
        assert user is None

        user = await repository.get_by_email("nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, db_session):
        """Test deleting user that doesn't exist"""
        repository = SQLAlchemyUserRepository(db_session)

        deleted = await repository.delete(UserId(999))
        assert deleted is False
