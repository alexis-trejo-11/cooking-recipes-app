from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.domain.interfaces import UserRepository
from app.auth.domain.user import User, UserRole, UserId
from app.auth.infrastucture.persitence.models import UserModel
from app.auth.application.exceptions import UserNotFoundException
import json


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._to_entity(user_model)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._to_entity(user_model)

    async def save(self, user: User) -> User:
        """Save user (create or update)"""
        if user.user_id and not user.user_id.is_zero():  # Update existing user
            return await self._update(user)
        else:  # Create new user
            return await self._create(user)

    async def _create(self, user: User) -> User:
        """Create new user"""
        user_model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            phone_number=user.phone_number,
            is_active=user.is_active,
            joined_at=user.joined_at,
            last_login=user.last_login,
            roles=json.dumps([role.value for role in user.roles]),
        )

        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        await self.session.commit()

        user._user_id = UserId(user_model.id)
        return user

    async def _update(self, user: User) -> User:
        """Update existing user"""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.user_id.value)
            .values(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                phone_number=user.phone_number,
                is_active=user.is_active,
                last_login=user.last_login,
                roles=json.dumps([role.value for role in user.roles]),
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount == 0:
            raise UserNotFoundException(f"User with ID {user.user_id} not found")

        return user

    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID"""
        stmt = delete(UserModel).where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination"""
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()

        return [self._to_entity(model) for model in user_models]

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_id(self, user_id: UserId) -> bool:
        stmt = select(UserModel.id).where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity"""
        # Parse roles from JSON string
        try:
            roles_data = json.loads(user_model.roles)
            roles = [UserRole(role) for role in roles_data]
        except (json.JSONDecodeError, ValueError):
            # Fallback to common user if roles are invalid
            roles = [UserRole.COMMON_USER]

        return User.reconstruct(
            {
                "user_id": UserId(user_model.id),
                "first_name": user_model.first_name,
                "last_name": user_model.last_name,
                "email": user_model.email,
                "password": user_model.password,
                "phone_number": user_model.phone_number,
                "roles": roles,
                "joined_at": user_model.joined_at,
                "last_login": user_model.last_login,
                "is_active": user_model.is_active,
            }
        )
