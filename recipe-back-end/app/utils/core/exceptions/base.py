from typing import Any, Dict, Optional
import uuid
from datetime import datetime
import traceback


class BaseAppException(Exception):
    """Base exception for the entire application"""

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())

        # Capture stack trace for logging
        self.stack_trace = traceback.format_exc()

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": {
                "id": self.error_id,
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp.isoformat(),
            }
        }

    def to_log_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging with full context"""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
        }


class ClientException(BaseAppException):
    """Base exception for client errors (4xx)"""

    def __init__(
        self,
        message: str = "Client error",
        error_code: str = "CLIENT_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class ServerException(BaseAppException):
    """Base exception for server errors (5xx)"""

    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)
