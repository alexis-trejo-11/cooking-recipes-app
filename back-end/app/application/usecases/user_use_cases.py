from typing import List, Optional
from ..dto.auth_dtos import UserResponse, UpdateUserRequest
from ..interfaces.user_repository import UserRepository
from app.application.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    AuthorizationException,
)
from app.domain.entities.user import User, UserRole, UserId
from app.domain.exceptions.user_exceptions import UserUpdateException


class GetUserUseCase:
    """Use case to get user by ID"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UserId) -> UserResponse:
        """Execute get user by ID"""

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        return UserResponse(
            user_id=str(user.user_id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            roles=[role.value for role in user.roles],
            is_active=user.is_active,
            joined_at=user.joined_at,
            last_login=user.last_login,
        )


class UpdateUserUseCase:
    """Use case to update user"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self,
        user_id: UserId,
        request: UpdateUserRequest,
        current_user_id: Optional[UserId] = None,
    ) -> UserResponse:
        """Execute user update"""

        # Authorization: users can only update their own profile unless they're admin
        if current_user_id and current_user_id != user_id:
            current_user = await self.user_repository.get_by_id(current_user_id)
            if not current_user or UserRole.ADMIN not in current_user.roles:
                raise AuthorizationException("Not authorized to update this user")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        try:
            if request.first_name is not None or request.last_name is not None:
                new_first_name = request.first_name or user.first_name
                new_last_name = request.last_name or user.last_name
                user.update_names(new_first_name, new_last_name)

            if request.phone_number is not None:
                user.update_phone_number(request.phone_number)

            updated_user = await self.user_repository.save(user)

            return UserResponse(
                user_id=str(updated_user.user_id),
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                email=updated_user.email,
                phone_number=updated_user.phone_number,
                roles=[role.value for role in updated_user.roles],
                is_active=updated_user.is_active,
                joined_at=updated_user.joined_at,
                last_login=updated_user.last_login,
            )

        except UserUpdateException as e:
            raise UserUpdateException(f"Failed to update user: {str(e)}") from e


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
                user_id=str(user.user_id),
                first_name=user.first_name,
                last_name=user.last_name,
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

        # Authorization: users can only delete their own account or admin can delete any
        if current_user_id and current_user_id != user_id:
            current_user = await self.user_repository.get_by_id(current_user_id)
            if not current_user or UserRole.ADMIN not in current_user.roles:
                raise AuthorizationException("Not authorized to delete this user")

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
    ) -> UserResponse:
        """Execute role change"""

        # Authorization: only admin can change roles
        current_user = await self.user_repository.get_by_id(current_user_id)
        if not current_user or UserRole.ADMIN not in current_user.roles:
            raise AuthorizationException("Not authorized to change user roles")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Update roles (this is a simplified implementation)
        # You might want to add more complex role management logic
        user._roles = new_roles
        updated_user = await self.user_repository.save(user)

        return UserResponse(
            user_id=str(updated_user.user_id),
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            phone_number=updated_user.phone_number,
            roles=[role.value for role in updated_user.roles],
            is_active=updated_user.is_active,
            joined_at=updated_user.joined_at,
            last_login=updated_user.last_login,
        )
