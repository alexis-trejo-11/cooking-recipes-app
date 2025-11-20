# app/config/rate_limiter.py
from fastapi import Request
from typing import Dict
import time
from collections import defaultdict
from app.utils.core.exceptions.base import RateLimitException


# Global rate limit configuration - NOW IN MINUTES
RATE_LIMIT_CONFIG = {
    "default": {"max_requests": 60, "window_seconds": 60},  # 60 requests per minute
    "strict": {"max_requests": 10, "window_seconds": 60},  # 10 requests per minute
    "generous": {"max_requests": 120, "window_seconds": 60},  # 120 requests per minute
    "public": {"max_requests": 100, "window_seconds": 60},  # 100 requests per minute
    "sensitive": {"max_requests": 5, "window_seconds": 60},  # 5 requests per minute
    # New more granular configurations
    "login": {"max_requests": 5, "window_seconds": 60},  # 5 login attempts per minute
    "registration": {
        "max_requests": 3,
        "window_seconds": 60,
    },  # 3 registrations per minute
    "api": {"max_requests": 30, "window_seconds": 60},  # 30 API calls per minute
}


class RateLimitManager:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.endpoint_configs = {}

    def set_endpoint_limit(self, endpoint: str, config_name: str):
        """Associate an endpoint with a rate limit configuration."""
        self.endpoint_configs[endpoint] = config_name

    def get_limit_config(self, endpoint: str) -> Dict:
        """Get rate limit configuration for an endpoint."""
        config_name = self.endpoint_configs.get(endpoint, "default")
        return RATE_LIMIT_CONFIG.get(config_name, RATE_LIMIT_CONFIG["default"])

    async def check_rate_limit(self, request: Request, endpoint: str):
        """
        Check if the current request exceeds the rate limit.

        Args:
            request: FastAPI Request object
            endpoint: Endpoint identifier

        Raises:
            RateLimitException: If rate limit is exceeded
        """
        if not endpoint:
            endpoint = request.url.path

        config = self.get_limit_config(endpoint)
        client_ip = request.client.host
        current_time = time.time()

        # Create unique key for this endpoint and client
        key = f"{endpoint}:{client_ip}"

        # Clean up old requests outside the current time window
        window_start = current_time - config["window_seconds"]
        self.request_counts[key] = [
            ts for ts in self.request_counts[key] if ts > window_start
        ]

        # Check if rate limit is exceeded
        if len(self.request_counts[key]) >= config["max_requests"]:
            # Calculate when the rate limit will reset
            oldest_request = (
                min(self.request_counts[key])
                if self.request_counts[key]
                else current_time
            )
            reset_time = oldest_request + config["window_seconds"]
            seconds_until_reset = int(reset_time - current_time)

            raise RateLimitException(
                message=f"Rate limit exceeded: {config['max_requests']} requests per {config['window_seconds']} seconds",
                details={
                    "max_requests": config["max_requests"],
                    "window_seconds": config["window_seconds"],
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "retry_after": seconds_until_reset,
                    "reset_time": reset_time,
                },
                context={
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "user_agent": request.headers.get("user-agent"),
                    "current_requests": len(self.request_counts[key]),
                },
            )

        # Add current request to the count
        self.request_counts[key].append(current_time)
        return True

    def get_rate_limit_info(self, endpoint: str, client_ip: str) -> Dict:
        """
        Get current rate limit information for debugging or client headers.

        Returns:
            Dict with rate limit information
        """
        config = self.get_limit_config(endpoint)
        key = f"{endpoint}:{client_ip}"
        current_time = time.time()

        # Clean up old requests
        window_start = current_time - config["window_seconds"]
        self.request_counts[key] = [
            ts for ts in self.request_counts[key] if ts > window_start
        ]

        return {
            "limit": config["max_requests"],
            "remaining": max(0, config["max_requests"] - len(self.request_counts[key])),
            "reset": int(current_time + config["window_seconds"]),
            "window_seconds": config["window_seconds"],
            "current_requests": len(self.request_counts[key]),
        }


# Global rate limit manager instance
rate_limit_manager = RateLimitManager()


def rate_limit(config_name: str = "default"):
    """
    Decorator to apply rate limiting to FastAPI endpoints.

    Args:
        config_name: Name of the rate limit configuration to use

    Example:
        @rate_limit("sensitive")
        @rate_limit("public")
        @rate_limit("strict")
    """

    def decorator(func):
        # Use the function's qualified name as endpoint identifier
        endpoint = f"{func.__module__}.{func.__name__}"
        rate_limit_manager.set_endpoint_limit(endpoint, config_name)
        func._rate_limit_config = config_name

        # Store rate limit info for potential use in response headers
        func._rate_limit_info = {
            "config_name": config_name,
            "max_requests": RATE_LIMIT_CONFIG[config_name]["max_requests"],
            "window_seconds": RATE_LIMIT_CONFIG[config_name]["window_seconds"],
        }

        return func

    return decorator


# Utility function to get rate limit headers for client information
def get_rate_limit_headers(request: Request, endpoint: str) -> Dict[str, str]:
    """
    Generate rate limit headers for client consumption.

    Returns:
        Dict with standard rate limit headers
    """
    client_ip = request.client.host
    info = rate_limit_manager.get_rate_limit_info(endpoint, client_ip)

    return {
        "X-RateLimit-Limit": str(info["limit"]),
        "X-RateLimit-Remaining": str(info["remaining"]),
        "X-RateLimit-Reset": str(info["reset"]),
        "X-RateLimit-Window": f"{info['window_seconds']}s",
    }
