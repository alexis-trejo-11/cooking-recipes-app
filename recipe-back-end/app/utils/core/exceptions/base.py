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
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
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


class DomainException(BaseAppException):
    """Base exception for domain errors (4xx)"""

    def __init__(
        self,
        message: str = "Domain error occurred",
        error_code: str = "DOMAIN_ERROR",
        status_code: int = 422,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class ApplicationException(BaseAppException):
    """Base exception for application errors (4xx)"""

    def __init__(
        self,
        message: str = "Application error occurred",
        error_code: str = "APPLICATION_ERROR",
        status_code: int = 422,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class NotFoundException(BaseAppException):
    """Base exception for not found errors (404)"""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        status_code: int = 404,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class SecurityException(BaseAppException):
    """Base exception for security-related errors"""

    def __init__(
        self,
        message: str = "Security error occurred",
        error_code: str = "SECURITY_ERROR",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, status_code, details, context)


class RateLimitException(BaseAppException):
    """Base exception for rate limiting errors (429)"""

    def __init__(
        self,
        message: str = "Too many requests",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        status_code: int = 429,
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
