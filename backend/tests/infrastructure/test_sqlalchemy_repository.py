from app.modules.auth.infrastucture.persitence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.modules.auth.domain.user import User, UserRole, UserId, UserGender
from app.config.sql_session import Base


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create async session for testing"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_user():
    """Create sample user for testing"""
    return User.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        raw_password="SecurePass123!",
        gender=UserGender.MALE,
        roles=[UserRole.COMMON_USER],
    )


class TestSQLAlchemyUserRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_user(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)
        retrieved_user = await repository.get_by_id(saved_user.id)

        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.first_name == sample_user.first_name
        assert retrieved_user.gender == UserGender.MALE
        assert retrieved_user.id.value == saved_user.id.value

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)
        retrieved_user = await repository.get_by_email(saved_user.email)

        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.first_name == sample_user.first_name

    @pytest.mark.asyncio
    async def test_exists_by_email(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        assert await repository.exists_by_email(sample_user.email) is False

        await repository.save(sample_user)

        assert await repository.exists_by_email(sample_user.email) is True
        assert await repository.exists_by_email("nonexistent@example.com") is False

    @pytest.mark.asyncio
    async def test_update_user(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)
        saved_user.update_names("Jane", "Smith")
        saved_user.update_email("jane.smith@example.com")

        await repository.save(saved_user)
        retrieved_user = await repository.get_by_id(saved_user.id)

        assert retrieved_user.first_name == "Jane"
        assert retrieved_user.last_name == "Smith"
        assert retrieved_user.email == "jane.smith@example.com"

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        saved_user = await repository.save(sample_user)
        assert await repository.exists_by_email(saved_user.email) is True

        deleted = await repository.delete(saved_user.id)
        assert deleted is True
        assert await repository.get_by_id(saved_user.id) is None
        assert await repository.exists_by_email(saved_user.email) is False

    @pytest.mark.asyncio
    async def test_list_users(self, db_session, sample_user):
        repository = SQLAlchemyUserRepository(db_session)

        assert len(await repository.list_all()) == 0

        await repository.save(sample_user)
        user2 = User.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            raw_password="SecurePass123!",
            gender=UserGender.FEMALE,
            roles=[UserRole.PREMIUM_USER],
        )
        await repository.save(user2)

        users = await repository.list_all()
        emails = [user.email for user in users]
        assert len(users) == 2
        assert "john.doe@example.com" in emails
        assert "jane.smith@example.com" in emails

    @pytest.mark.asyncio
    async def test_user_roles_persistence(self, db_session):
        repository = SQLAlchemyUserRepository(db_session)

        user = User.create(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            raw_password="SecurePass123!",
            gender=UserGender.OTHER,
            roles=[UserRole.ADMIN, UserRole.MODERATOR],
        )

        saved_user = await repository.save(user)
        retrieved_user = await repository.get_by_id(saved_user.id)

        assert UserRole.ADMIN in retrieved_user.roles
        assert UserRole.MODERATOR in retrieved_user.roles
        assert len(retrieved_user.roles) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db_session):
        repository = SQLAlchemyUserRepository(db_session)

        assert await repository.get_by_id(UserId(999)) is None
        assert await repository.get_by_email("nonexistent@example.com") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, db_session):
        repository = SQLAlchemyUserRepository(db_session)
        assert await repository.delete(UserId(999)) is False
