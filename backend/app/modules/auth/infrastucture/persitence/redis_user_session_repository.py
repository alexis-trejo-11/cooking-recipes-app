import json
from typing import Optional
import redis.asyncio as redis
from datetime import datetime, timezone
from app.modules.auth.domain.session import UserSession
from app.modules.auth.domain.interfaces import SessionRepository


class RedisSessionRepository(SessionRepository):
    """Redis implementation of SessionRepository"""

    def __init__(self, redis_client: redis.Redis, key_prefix: str = "session"):
        self.redis = redis_client
        self.key_prefix = key_prefix

    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"{self.key_prefix}:{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Generate Redis key for user's session list"""
        return f"{self.key_prefix}:user:{user_id}"

    def _refresh_token_key(self, refresh_token: str) -> str:
        """Generate Redis key for refresh token lookup"""
        return f"{self.key_prefix}:refresh:{refresh_token}"

    async def save_session(self, session: UserSession) -> None:
        """Save session to Redis with TTL"""
        session_key = self._session_key(session.session_id)
        user_sessions_key = self._user_sessions_key(session.user_id)
        refresh_token_key = self._refresh_token_key(session.refresh_token)

        # Calculate TTL in seconds
        ttl = int((session.expires_at - datetime.now(timezone.utc)).total_seconds())

        # Session data
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "refresh_token": session.refresh_token,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "created_at": (
                session.created_at.isoformat() if session.created_at else None
            ),
            "expires_at": (
                session.expires_at.isoformat() if session.expires_at else None
            ),
            "last_activity": (
                session.last_activity.isoformat() if session.last_activity else None
            ),
        }

        # Use pipeline for atomic operations
        async with self.redis.pipeline() as pipe:
            # Store session data
            pipe.setex(session_key, ttl, json.dumps(session_data, default=str))

            # Add session to user's session set
            pipe.sadd(user_sessions_key, session.session_id)
            pipe.expire(user_sessions_key, ttl)

            # Create refresh token -> session_id mapping
            pipe.setex(refresh_token_key, ttl, session.session_id)

            await pipe.execute()

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        session_key = self._session_key(session_id)
        data = await self.redis.get(session_key)

        if not data:
            return None

        session_dict = json.loads(data)
        return UserSession(
            session_id=session_dict["session_id"],
            user_id=session_dict["user_id"],
            refresh_token=session_dict["refresh_token"],
            device_info=session_dict.get("device_info"),
            ip_address=session_dict.get("ip_address"),
            user_agent=session_dict.get("user_agent"),
            created_at=(
                datetime.fromisoformat(session_dict["created_at"])
                if session_dict.get("created_at")
                else datetime.now(timezone.utc)
            ),
            expires_at=(
                datetime.fromisoformat(session_dict["expires_at"])
                if session_dict.get("expires_at")
                else datetime.now(timezone.utc)
            ),
            last_activity=(
                datetime.fromisoformat(session_dict["last_activity"])
                if session_dict.get("last_activity")
                else datetime.now(timezone.utc)
            ),
        )

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> Optional[UserSession]:
        """Get session by refresh token"""
        refresh_token_key = self._refresh_token_key(refresh_token)
        session_id = await self.redis.get(refresh_token_key)

        if not session_id:
            return None

        return await self.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        session = await self.get_session(session_id)
        if not session:
            return False

        session_key = self._session_key(session_id)
        user_sessions_key = self._user_sessions_key(session.user_id)
        refresh_token_key = self._refresh_token_key(session.refresh_token)

        async with self.redis.pipeline() as pipe:
            pipe.delete(session_key)
            pipe.srem(user_sessions_key, session_id)
            pipe.delete(refresh_token_key)
            results = await pipe.execute()

        return results[0] > 0

    async def delete_all_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user"""
        user_sessions_key = self._user_sessions_key(user_id)
        session_ids = await self.redis.smembers(user_sessions_key)

        if not session_ids:
            return 0

        deleted_count = 0
        for session_id in session_ids:
            session_id_str = session_id if isinstance(session_id, bytes) else session_id
            if await self.delete_session(session_id_str):
                deleted_count += 1

        # Clean up the user sessions set
        await self.redis.delete(user_sessions_key)

        return deleted_count

    async def update_last_activity(self, session_id: str) -> None:
        """Update session last activity timestamp"""
        session = await self.get_session(session_id)
        if not session:
            return

        session.last_activity = datetime.utcnow()
        await self.save_session(session)

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions (Redis TTL handles this automatically)"""
        # Redis automatically removes expired keys
        # This method is here for interface compatibility
        return 0
