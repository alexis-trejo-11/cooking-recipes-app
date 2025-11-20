from fastapi import Request
from typing import Dict
import time
from collections import defaultdict
from app.utils.core.exceptions.base import (
    RateLimitException,
)

# Configuración global de rate limits
RATE_LIMIT_CONFIG = {
    "default": {"max_requests": 100, "window_seconds": 3600},  # 100 requests per hour
    "strict": {"max_requests": 10, "window_seconds": 300},  # 10 requests per 5 minutes
    "generous": {
        "max_requests": 1000,
        "window_seconds": 3600,
    },  # 1000 requests per hour
    "public": {"max_requests": 500, "window_seconds": 3600},  # 500 requests per hour
    "sensitive": {"max_requests": 5, "window_seconds": 60},  # 5 requests per minute
}


class RateLimitManager:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.endpoint_configs = {}

    def set_endpoint_limit(self, endpoint: str, config_name: str):
        self.endpoint_configs[endpoint] = config_name

    def get_limit_config(self, endpoint: str) -> Dict:
        config_name = self.endpoint_configs.get(endpoint, "default")
        return RATE_LIMIT_CONFIG[config_name]

    async def check_rate_limit(self, request: Request, endpoint: str):
        if not endpoint:
            endpoint = request.url.path

        config = self.get_limit_config(endpoint)
        client_ip = request.client.host
        current_time = time.time()

        # Limpiar requests antiguos
        key = f"{endpoint}:{client_ip}"
        self.request_counts[key] = [
            ts
            for ts in self.request_counts[key]
            if current_time - ts < config["window_seconds"]
        ]

        # Verificar límite - Ahora usando tu excepción personalizada
        if len(self.request_counts[key]) >= config["max_requests"]:
            raise RateLimitException(
                message=f"Rate limit exceeded: {config['max_requests']} requests per {config['window_seconds']} seconds",
                details={
                    "max_requests": config["max_requests"],
                    "window_seconds": config["window_seconds"],
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                },
                context={
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "user_agent": request.headers.get("user-agent"),
                },
            )

        self.request_counts[key].append(current_time)
        return True


rate_limit_manager = RateLimitManager()


def rate_limit(config_name: str = "default"):
    def decorator(func):
        endpoint = f"{func.__module__}.{func.__name__}"
        rate_limit_manager.set_endpoint_limit(endpoint, config_name)
        func._rate_limit_config = config_name
        return func

    return decorator
