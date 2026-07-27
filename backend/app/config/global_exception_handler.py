"""
Enhanced Global Exception Handler with Pydantic models and better error handling
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError

from app.utils.core.exceptions.base import (
    BaseAppException,
    SecurityException,
    DomainException,
    ApplicationException,
    ServerException,
    RateLimitException,
    NotFoundException,
)

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Individual error detail"""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "type": "value_error",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional error details"
    )
    timestamp: Optional[str] = Field(
        None, description="ISO 8601 timestamp when error occurred"
    )
    error_id: Optional[str] = Field(
        None, description="Unique error identifier for tracking"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "validation_errors": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "type": "value_error.email",
                        }
                    ]
                },
                "timestamp": "2025-11-16T10:30:00Z",
                "error_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class ErrorResponseWrapper(BaseModel):
    """Wrapper for error response"""

    error: ErrorResponse

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "The requested resource was not found",
                    "details": {"resource_type": "user", "resource_id": "123"},
                    "timestamp": "2025-11-16T10:30:00Z",
                }
            }
        }


class GlobalExceptionHandler:
    """
    Centralized exception handler with:
    - Pydantic models for consistent error responses
    - Handling of common Python exceptions
    - Proper logging and sanitization
    - OpenAPI documentation support
    """

    def __init__(self, app: FastAPI, debug: bool = False):
        self.app = app
        self.debug = debug
        self._register_handlers()

    def _register_handlers(self):
        """Register all exception handlers in order of specificity"""

        # 1. Custom application exceptions (most specific)
        self.app.add_exception_handler(
            RateLimitException, self.handle_rate_limit_exception
        )
        self.app.add_exception_handler(
            SecurityException, self.handle_security_exception
        )
        self.app.add_exception_handler(
            NotFoundException, self.handle_not_found_exception
        )
        self.app.add_exception_handler(DomainException, self.handle_domain_exception)
        self.app.add_exception_handler(
            ApplicationException, self.handle_application_exception
        )
        self.app.add_exception_handler(ServerException, self.handle_server_exception)
        self.app.add_exception_handler(BaseAppException, self.handle_app_exception)

        # 2. FastAPI and Pydantic validation exceptions
        self.app.add_exception_handler(
            RequestValidationError, self.handle_validation_error
        )
        self.app.add_exception_handler(
            ValidationError, self.handle_pydantic_validation_error
        )

        # 3. FastAPI HTTP exceptions
        self.app.add_exception_handler(HTTPException, self.handle_http_exception)

        # 4. Common Python exceptions (before generic catch-all)
        self.app.add_exception_handler(ValueError, self.handle_value_error)
        self.app.add_exception_handler(TypeError, self.handle_type_error)
        self.app.add_exception_handler(KeyError, self.handle_key_error)
        self.app.add_exception_handler(AttributeError, self.handle_attribute_error)
        self.app.add_exception_handler(IndexError, self.handle_index_error)
        self.app.add_exception_handler(
            ZeroDivisionError, self.handle_zero_division_error
        )

        # 5. Generic exception handler (catch-all - least specific)
        self.app.add_exception_handler(Exception, self.handle_generic_exception)

    # Custom Application Exception Handlers

    async def handle_rate_limit_exception(
        self, request: Request, exc: RateLimitException
    ) -> JSONResponse:
        """Handle rate limiting exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Rate limit exceeded: {exc.error_code}", extra=log_context)

        # Track rate limit hits
        if hasattr(request.app.state, "metrics"):
            request.app.state.metrics.rate_limit_hits.inc()

        return self._create_error_response(exc)

    async def handle_not_found_exception(
        self, request: Request, exc: NotFoundException
    ) -> JSONResponse:
        """Handle not found exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.info(f"Resource not found: {exc.error_code}", extra=log_context)

        return self._create_error_response(exc)

    async def handle_security_exception(
        self, request: Request, exc: SecurityException
    ) -> JSONResponse:
        """Handle security exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Security violation: {exc.error_code}", extra=log_context)

        # Sanitize details in security errors
        sanitized_exc = self._sanitize_security_exception(exc)
        return self._create_error_response(sanitized_exc)

    async def handle_domain_exception(
        self, request: Request, exc: DomainException
    ) -> JSONResponse:
        """Handle domain exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Domain error: {exc.error_code}", extra=log_context)

        return self._create_error_response(exc)

    async def handle_application_exception(
        self, request: Request, exc: ApplicationException
    ) -> JSONResponse:
        """Handle application exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Application error: {exc.error_code}", extra=log_context)

        return self._create_error_response(exc)

    async def handle_server_exception(
        self, request: Request, exc: ServerException
    ) -> JSONResponse:
        """Handle server exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.error(
            f"Server error: {exc.error_code}", extra=log_context, exc_info=True
        )

        # Sanitize internal details in production
        if not self.debug:
            exc.details = self._sanitize_details(exc.details)

        return self._create_error_response(exc)

    async def handle_app_exception(
        self, request: Request, exc: BaseAppException
    ) -> JSONResponse:
        """Handle base application exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Application exception: {exc.error_code}", extra=log_context)

        return self._create_error_response(exc)

    # FastAPI Exception Handlers

    async def handle_http_exception(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""

        # Convert 429 to our custom RateLimitException
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            rate_limit_exc = RateLimitException(
                message=str(exc.detail) if exc.detail else "Too many requests",
                details={"path": str(request.url.path)},
                context=self._get_request_context(request),
            )
            return await self.handle_rate_limit_exception(request, rate_limit_exc)

        # Convert to ApplicationException
        app_exc = ApplicationException(
            message=str(exc.detail) if exc.detail else "An error occurred",
            error_code=f"HTTP_{exc.status_code}",
            status_code=exc.status_code,
            details={},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, app_exc)
        logger.warning(f"HTTP exception: {exc.status_code}", extra=log_context)

        return self._create_error_response(app_exc)

    async def handle_validation_error(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request validation errors"""
        error_details = []

        for error in exc.errors():
            error_details.append(
                {
                    "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
                    "message": error.get("msg", "Validation error"),
                    "type": error.get("type", "unknown"),
                }
            )

        validation_exc = ApplicationException(
            message="Request validation failed",
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": error_details},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, validation_exc)
        logger.warning("Request validation failed", extra=log_context)

        return self._create_error_response(validation_exc)

    async def handle_pydantic_validation_error(
        self, request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        error_details = []

        for error in exc.errors():
            error_details.append(
                {
                    "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
                    "message": error.get("msg", "Validation error"),
                    "type": error.get("type", "unknown"),
                }
            )

        validation_exc = ApplicationException(
            message="Data validation failed",
            error_code="PYDANTIC_VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": error_details},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, validation_exc)
        logger.warning("Pydantic validation failed", extra=log_context)

        return self._create_error_response(validation_exc)

    # Common Python Exception Handlers

    async def handle_value_error(
        self, request: Request, exc: ValueError
    ) -> JSONResponse:
        """Handle ValueError exceptions"""
        app_exc = ApplicationException(
            message="Invalid value provided",
            error_code="VALUE_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"error": str(exc) if self.debug else "Invalid input value"},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, app_exc, original_exc=exc)
        logger.warning("ValueError occurred", extra=log_context)

        return self._create_error_response(app_exc)

    async def handle_type_error(self, request: Request, exc: TypeError) -> JSONResponse:
        """Handle TypeError exceptions"""
        app_exc = ApplicationException(
            message="Invalid type provided",
            error_code="TYPE_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"error": str(exc) if self.debug else "Invalid data type"},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, app_exc, original_exc=exc)
        logger.error("TypeError occurred", extra=log_context, exc_info=True)

        return self._create_error_response(app_exc)

    async def handle_key_error(self, request: Request, exc: KeyError) -> JSONResponse:
        """Handle KeyError exceptions"""
        app_exc = ApplicationException(
            message="Required key not found",
            error_code="KEY_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={
                "missing_key": str(exc) if self.debug else "Required field missing"
            },
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, app_exc, original_exc=exc)
        logger.warning("KeyError occurred", extra=log_context)

        return self._create_error_response(app_exc)

    async def handle_attribute_error(
        self, request: Request, exc: AttributeError
    ) -> JSONResponse:
        """Handle AttributeError exceptions"""
        server_exc = ServerException(
            message="Internal server error",
            error_code="ATTRIBUTE_ERROR",
            details={"error": str(exc) if self.debug else {}},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, server_exc, original_exc=exc)
        logger.error("AttributeError occurred", extra=log_context, exc_info=True)

        return self._create_error_response(server_exc)

    async def handle_index_error(
        self, request: Request, exc: IndexError
    ) -> JSONResponse:
        """Handle IndexError exceptions"""
        server_exc = ServerException(
            message="Internal server error",
            error_code="INDEX_ERROR",
            details={"error": str(exc) if self.debug else {}},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, server_exc, original_exc=exc)
        logger.error("IndexError occurred", extra=log_context, exc_info=True)

        return self._create_error_response(server_exc)

    async def handle_zero_division_error(
        self, request: Request, exc: ZeroDivisionError
    ) -> JSONResponse:
        """Handle ZeroDivisionError exceptions"""
        server_exc = ServerException(
            message="Internal server error",
            error_code="DIVISION_BY_ZERO",
            details={"error": str(exc) if self.debug else {}},
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, server_exc, original_exc=exc)
        logger.error("ZeroDivisionError occurred", extra=log_context, exc_info=True)

        return self._create_error_response(server_exc)

    async def handle_generic_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle any unhandled exceptions - catch-all handler"""
        server_exc = ServerException(
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=(
                {}
                if not self.debug
                else {
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            ),
            context={"path": str(request.url.path)},
        )

        log_context = self._build_log_context(request, server_exc, original_exc=exc)
        logger.critical(
            f"Unhandled exception: {type(exc).__name__}",
            extra=log_context,
            exc_info=True,
        )

        return self._create_error_response(server_exc)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _create_error_response(self, exc: BaseAppException) -> JSONResponse:
        """Create standardized error response"""
        error_response = ErrorResponseWrapper(
            error=ErrorResponse(
                code=exc.error_code,
                message=exc.message,
                details=exc.details if exc.details else {},
                timestamp=(
                    exc.timestamp.isoformat()
                    if hasattr(exc, "timestamp")
                    else datetime.utcnow().isoformat()
                ),
                error_id=exc.error_id if hasattr(exc, "error_id") else None,
            )
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(exclude_none=True),
        )

    def _build_log_context(
        self,
        request: Request,
        exc: BaseAppException,
        original_exc: Optional[Exception] = None,
    ) -> Dict[str, Any]:
        """Build context dictionary for logging"""
        context = {
            "error_id": getattr(exc, "error_id", None),
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Add exception context if available
        if hasattr(exc, "context") and exc.context:
            context.update(exc.context)

        # Add original exception info if available
        if original_exc:
            context.update(
                {
                    "original_exception_type": type(original_exc).__name__,
                    "original_exception_message": str(original_exc),
                }
            )

        return context

    def _get_request_context(self, request: Request) -> Dict[str, Any]:
        """Extract context from request"""
        return {
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "method": request.method,
            "path": str(request.url.path),
        }

    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from error details"""
        if not details:
            return {}

        # List of sensitive keys to remove
        sensitive_keys = {
            "password",
            "token",
            "secret",
            "api_key",
            "private_key",
            "credit_card",
            "ssn",
            "internal",
            "stack_trace",
            "traceback",
        }

        sanitized = {}
        for key, value in details.items():
            if key.lower() not in sensitive_keys:
                if isinstance(value, dict):
                    sanitized[key] = self._sanitize_details(value)
                else:
                    sanitized[key] = value

        return sanitized

    def _sanitize_security_exception(self, exc: SecurityException) -> SecurityException:
        """Sanitize security exception details"""
        # Don't expose detailed security information
        sanitized_details = {"hint": "Authentication or authorization failed"}

        exc.details = sanitized_details if not self.debug else exc.details
        return exc
