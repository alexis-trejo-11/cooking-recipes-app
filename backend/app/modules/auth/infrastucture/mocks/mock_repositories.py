from typing import Optional, List, Dict
from app.modules.auth.domain.interfaces import UserRepository, SessionRepository
from app.modules.auth.domain.user import User, UserId, UserRecipeStats
from app.modules.auth.domain.session import UserSession


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing"""

    def __init__(self):
        self._users: Dict[UserId, User] = {}
        self._email_index: Dict[str, UserId] = {}
        self._phone_index: Dict[str, UserId] = {}
        self._next_id = 1

    async def get_by_id(self, id: UserId) -> Optional[User]:
        return self._users.get(id)

    async def get_by_email(self, email: str) -> Optional[User]:
        user_id = self._email_index.get(email.lower())
        return self._users.get(user_id) if user_id else None

    async def save(self, user: User) -> User:
        if user.id.is_zero():
            new_id = UserId(self._next_id)
            self._next_id += 1
            user._user_id = new_id

        self._users[user.id] = user
        self._email_index[user.email.lower()] = user.id
        if user.phone_number:
            self._phone_index[user.phone_number] = user.id
        return user

    async def delete(self, id: UserId) -> bool:
        if id in self._users:
            user = self._users[id]
            del self._email_index[user.email.lower()]
            if user.phone_number and user.phone_number in self._phone_index:
                del self._phone_index[user.phone_number]
            del self._users[id]
            return True
        return False

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = list(self._users.values())
        return users[skip : skip + limit]

    async def exists_by_email(self, email: str) -> bool:
        return email.lower() in self._email_index

    async def exists_by_id(self, id: UserId) -> bool:
        return id in self._users

    async def exists_by_phone(self, phone: str) -> bool:
        return phone in self._phone_index

    async def get_recipe_stats(self, id: UserId) -> UserRecipeStats:
        return UserRecipeStats()


class MockSessionRepository(SessionRepository):
    """In-memory session store for auth use-case tests."""

    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
        self._by_refresh: Dict[str, str] = {}

    async def save_session(self, session: UserSession) -> None:
        self._sessions[session.session_id] = session
        self._by_refresh[session.refresh_token] = session.session_id

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        return self._sessions.get(session_id)

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[UserSession]:
        session_id = self._by_refresh.get(refresh_token)
        return self._sessions.get(session_id) if session_id else None

    async def delete_session(self, session_id: str) -> bool:
        session = self._sessions.pop(session_id, None)
        if not session:
            return False
        self._by_refresh.pop(session.refresh_token, None)
        return True

    async def delete_all_user_sessions(self, user_id: str) -> int:
        to_delete = [
            sid for sid, s in self._sessions.items() if s.user_id == user_id
        ]
        for sid in to_delete:
            await self.delete_session(sid)
        return len(to_delete)

    async def update_last_activity(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = session.last_activity

    async def cleanup_expired_sessions(self) -> int:
        return 0
