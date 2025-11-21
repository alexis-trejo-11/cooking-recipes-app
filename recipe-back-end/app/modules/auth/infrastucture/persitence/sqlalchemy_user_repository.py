from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.domain.interfaces import UserRepository
from app.modules.auth.domain.user import (
    User,
    UserGender,
    UserRole,
    UserId,
    UserRecipeStats,
)
from app.modules.auth.infrastucture.persitence.models import UserModel
from app.modules.auth.application.exceptions import UserNotFoundException
import json
from app.modules.recipe.infrastructure.persistence.models import (
    recipe_favorites,
    ReviewModel,
    RecipeModel,
)


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UserId) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == id.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._to_entity(user_model)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            return None

        return self._to_entity(user_model)

    async def save(self, user: User) -> User:
        """Save user (create or update)"""
        if user.id and not user.id.is_zero():  # Update existing user
            return await self._update(user)
        else:  # Create new user
            return await self._create(user)

    async def _create(self, user: User) -> User:
        """Create new user"""
        user_model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            date_of_birth=user.date_of_birth,
            gender=user.gender.value,
            profile_picture_url=user.profile_picture_url,
            bio=user.bio,
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
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                date_of_birth=user.date_of_birth,
                gender=user.gender.value,
                profile_picture_url=user.profile_picture_url,
                bio=user.bio,
                phone_number=user.phone_number,
                is_active=user.is_active,
                last_login=user.last_login,
                roles=json.dumps([role.value for role in user.roles]),
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount == 0:
            raise UserNotFoundException(f"User with ID {user.id} not found")

        return user

    async def delete(self, id: UserId) -> bool:
        """Delete user by ID"""
        stmt = delete(UserModel).where(UserModel.id == id.value)
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

    async def exists_by_id(self, id: UserId) -> bool:
        stmt = select(UserModel.id).where(UserModel.id == id.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_phone(self, phone: str) -> bool:
        """Check if user exists by phone number"""
        stmt = select(UserModel.id).where(UserModel.phone_number == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_recipe_stats(self, id: UserId) -> UserRecipeStats:
        """Get user recipe statistics"""
        # Count favorite recipes
        fav_stmt = select(recipe_favorites.c.user_id).where(
            recipe_favorites.c.user_id == id.value
        )
        fav_result = await self.session.execute(fav_stmt)
        favorite_count = len(fav_result.fetchall())

        # Count reviewed recipes
        rev_stmt = select(ReviewModel.user_id).where(ReviewModel.user_id == id.value)
        rev_result = await self.session.execute(rev_stmt)
        reviewed_count = len(rev_result.fetchall())

        # Count created recipes
        create_stmt = select(RecipeModel).where(RecipeModel.author_id == id.value)
        create_result = await self.session.execute(create_stmt)
        created_count = len(create_result.scalars().all())

        return UserRecipeStats(
            favorite_recipes_count=favorite_count,
            reviewed_recipes_count=reviewed_count,
            created_recipes_count=created_count,
        )

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
                "id": UserId(user_model.id),
                "first_name": user_model.first_name,
                "last_name": user_model.last_name,
                "email": user_model.email,
                "password": user_model.password,
                "phone_number": user_model.phone_number,
                "date_of_birth": user_model.date_of_birth,
                "profile_picture_url": user_model.profile_picture_url,
                "bio": user_model.bio,
                "gender": (
                    UserGender(user_model.gender)
                    if user_model.gender
                    else UserGender.UNKNOWN
                ),
                "roles": roles,
                "joined_at": user_model.joined_at,
                "last_login": user_model.last_login,
                "is_active": user_model.is_active,
            }
        )
