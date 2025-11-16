from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Protocol


@dataclass
class UserSession:
    """Represents a user session"""

    session_id: str
    user_id: str
    refresh_token: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    expires_at: datetime = datetime.now(timezone.utc)
    last_activity: datetime = datetime.now(timezone.utc)
