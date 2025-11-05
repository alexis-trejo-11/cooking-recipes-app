from typing import Optional, List, Dict
from app.auth.domain.interfaces import UserRepository
from app.auth.domain.user import User, UserId


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing"""

    def __init__(self):
        self._users: Dict[UserId, User] = {}
        self._email_index: Dict[str, UserId] = {}

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        user_id = self._email_index.get(email.lower())
        return self._users.get(user_id) if user_id else None

    async def save(self, user: User) -> User:
        if not user.user_id:
            # Generate new ID for new users
            new_id = UserId(len(self._users) + 1)
            user._user_id = new_id

        self._users[user.user_id] = user
        self._email_index[user.email.lower()] = user.user_id
        return user

    async def delete(self, user_id: UserId) -> bool:
        if user_id in self._users:
            user = self._users[user_id]
            del self._email_index[user.email.lower()]
            del self._users[user_id]
            return True
        return False

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = list(self._users.values())
        return users[skip : skip + limit]

    async def exists_by_email(self, email: str) -> bool:
        return email.lower() in self._email_index
