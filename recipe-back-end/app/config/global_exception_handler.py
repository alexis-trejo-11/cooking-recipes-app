import logging
from typing import Any, Dict, Union
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.utils.core.exceptions.base import (
    BaseAppException,
    SecurityException,
    DomainException,
    ApplicationException,
    ServerException,
    RateLimitException,
)
from app.utils.core.exceptions.modules import *

# Configure logger
logger = logging.getLogger("app.exceptions")


class GlobalExceptionHandler:
    def __init__(self, app: FastAPI, debug: bool = False):
        self.app = app
        self.debug = debug
        self._register_handlers()

    def _register_handlers(self):
        """Register all exception handlers"""
        # Custom application exceptions
        self.app.add_exception_handler(BaseAppException, self.handle_app_exception)
        self.app.add_exception_handler(ServerException, self.handle_server_exception)
        self.app.add_exception_handler(
            SecurityException, self.handle_security_exception
        )
        self.app.add_exception_handler(DomainException, self.handle_domain_exception)
        self.app.add_exception_handler(
            ApplicationException, self.handle_application_exception
        )

        # Rate limiting exception
        self.app.add_exception_handler(
            RateLimitException, self.handle_rate_limit_exception
        )

        # FastAPI and Pydantic exceptions
        self.app.add_exception_handler(
            RequestValidationError, self.handle_validation_error
        )
        self.app.add_exception_handler(ValidationError, self.handle_validation_error)

        # HTTPException general (incluye rate limiting de FastAPI)
        self.app.add_exception_handler(HTTPException, self.handle_http_exception)

        # Generic exception handler (catch-all)
        self.app.add_exception_handler(Exception, self.handle_generic_exception)

    async def handle_rate_limit_exception(
        self, request: Request, exc: RateLimitException
    ) -> JSONResponse:
        """Handle rate limiting exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Rate limit exceeded: {exc.error_code}", extra=log_context)

        # Incrementar estadísticas de rate limiting si las tienes
        if hasattr(request.app, "app_stats"):
            request.app.app_stats["blocked_requests"] += 1

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": (
                        exc.timestamp.isoformat() if hasattr(exc, "timestamp") else None
                    ),
                    "error_id": exc.error_id if hasattr(exc, "error_id") else None,
                }
            },
        )

    async def handle_http_exception(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle generic HTTP exceptions, including rate limiting"""
        # Si es un error 429 (Rate Limiting) pero no es nuestra excepción personalizada
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            # Convertir a nuestra excepción personalizada
            rate_limit_exc = RateLimitException(
                message=str(exc.detail),
                details={"limit_details": exc.detail, "path": request.url.path},
                context={
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
            return await self.handle_rate_limit_exception(request, rate_limit_exc)

        # Para otros HTTP exceptions, crear una ApplicationException
        app_exc = ApplicationException(
            message=str(exc.detail),
            error_code=f"HTTP_{exc.status_code}",
            status_code=exc.status_code,
            context={"path": request.url.path},
        )

        return await self.handle_application_exception(request, app_exc)

    # Tus handlers existentes se mantienen igual...
    async def handle_app_exception(
        self, request: Request, exc: BaseAppException
    ) -> JSONResponse:
        """Handle custom application exceptions"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Application exception: {exc.error_code}", extra=log_context)

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    async def handle_security_exception(
        self, request: Request, exc: SecurityException
    ) -> JSONResponse:
        """Handle security exceptions (4xx)"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Security error: {exc.error_code}", extra=log_context)

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    async def handle_domain_exception(
        self, request: Request, exc: DomainException
    ) -> JSONResponse:
        """Handle domain exceptions (4xx)"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Domain error: {exc.error_code}", extra=log_context)

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    async def handle_application_exception(
        self, request: Request, exc: ApplicationException
    ) -> JSONResponse:
        """Handle application exceptions (4xx)"""
        log_context = self._build_log_context(request, exc)
        logger.warning(f"Application error: {exc.error_code}", extra=log_context)

        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    async def handle_server_exception(
        self, request: Request, exc: ServerException
    ) -> JSONResponse:
        """Handle server exceptions (5xx)"""
        log_context = self._build_log_context(request, exc)
        logger.error(
            f"Server error: {exc.error_code}", extra=log_context, exc_info=True
        )

        response_content = exc.to_dict()
        if not self.debug:
            # Hide internal details in production
            response_content["error"]["details"] = {}
            if "internal" in response_content["error"]["details"]:
                del response_content["error"]["details"]["internal"]

        return JSONResponse(status_code=exc.status_code, content=response_content)

    async def handle_validation_error(
        self, request: Request, exc: Union[RequestValidationError, ValidationError]
    ) -> JSONResponse:
        """Handle request validation errors"""
        error_details = []
        if hasattr(exc, "errors"):
            for error in exc.errors():
                error_details.append(
                    {
                        "field": " -> ".join(
                            [str(loc) for loc in error.get("loc", [])]
                        ),
                        "message": error.get("msg"),
                        "type": error.get("type"),
                    }
                )

        validation_exc = ApplicationException(
            message="Request validation failed",
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": error_details},
            context={"path": request.url.path},
        )

        log_context = self._build_log_context(request, validation_exc)
        logger.warning("Request validation failed", extra=log_context)

        return JSONResponse(
            status_code=validation_exc.status_code, content=validation_exc.to_dict()
        )

    async def handle_generic_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle any unhandled exceptions"""
        internal_exc = ServerException(
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
            context={"path": request.url.path},
        )

        log_context = self._build_log_context(request, internal_exc, original_exc=exc)
        logger.critical(
            f"Unhandled exception: {type(exc).__name__}",
            extra=log_context,
            exc_info=True,
        )

        response_content = internal_exc.to_dict()
        if self.debug:
            response_content["error"]["internal"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }

        return JSONResponse(
            status_code=internal_exc.status_code, content=response_content
        )

    def _build_log_context(
        self,
        request: Request,
        exc: BaseAppException,
        original_exc: Optional[Exception] = None,
    ) -> Dict[str, Any]:
        """Build context dictionary for logging"""
        context = {
            "error_id": exc.error_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Add exception context if available
        if exc.context:
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
