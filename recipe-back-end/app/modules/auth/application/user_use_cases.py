from typing import List, Optional
from .dtos import UserProfileResponse, UpdateUserProfileRequest, UserResponse
from app.modules.auth.domain.interfaces import UserRepository
from app.modules.auth.application.exceptions import (
    UserNotFoundException,
    AuthAppException as AuthorizationException,
)
from app.modules.auth.domain.user import User, UserRole, UserId


class GetUserProfileUseCase:
    """Use case to get user by ID"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user: User) -> UserProfileResponse:
        """Execute get user by ID"""
        stats = await self.user_repository.get_recipe_stats(user.id)

        return UserProfileResponse.from_user_and_stats(user, stats)


class UpdateUserProfileUseCase:
    """Use case to update user"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self,
        user_id: UserId,
        request: UpdateUserProfileRequest,
    ) -> None:
        """Execute user update"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        if request.first_name is not None or request.last_name is not None:
            new_first_name = request.first_name or user.first_name
            new_last_name = request.last_name or user.last_name
            user.update_names(new_first_name, new_last_name)

        if request.phone_number is not None:
            user.update_phone_number(request.phone_number)

        await self.user_repository.save(user)


class ListUsersUseCase:
    """Use case to list users"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, skip: int = 0, limit: int = 100, current_user_id: Optional[UserId] = None
    ) -> List[UserResponse]:
        """Execute list users"""

        # Optional: Add an authorization check for admin only
        if current_user_id:
            current_user = await self.user_repository.get_by_id(current_user_id)
            if current_user and UserRole.ADMIN not in current_user.roles:
                raise AuthorizationException("Not authorized to list users")

        users = await self.user_repository.list_all(skip=skip, limit=limit)

        return [
            UserResponse(
                user_id=str(user.id),
                full_name=f"{user.first_name} {user.last_name}",
                email=user.email,
                phone_number=user.phone_number,
                roles=[role.value for role in user.roles],
                is_active=user.is_active,
                joined_at=user.joined_at,
                last_login=user.last_login,
            )
            for user in users
        ]


class DeleteUserUseCase:
    """Use case to delete user"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: UserId, current_user_id: Optional[UserId] = None
    ) -> bool:
        """Execute user deletion"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Prevent self-deletion for admin users if needed
        if current_user_id == user_id and UserRole.ADMIN in user.roles:
            # Add additional checks if needed
            pass

        return await self.user_repository.delete(user_id)


class ChangeUserRoleUseCase:
    """Use case to change user roles (admin only)"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, user_id: UserId, new_roles: List[UserRole], current_user_id: UserId
    ) -> None:
        """Execute role change"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        user._roles = new_roles
        await self.user_repository.save(user)
