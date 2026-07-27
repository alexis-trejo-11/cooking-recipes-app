# app/config/redis_config.py
from pydantic_settings import BaseSettings
from typing import Optional
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)


class RedisSettings(BaseSettings):
    """Redis configuration settings"""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    REDIS_SESSION_PREFIX: str = "session:"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

_redis_client: Optional[redis.Redis] = None
redis_settings = RedisSettings()


async def initialize_redis():
    """Initialize global Redis client"""
    global _redis_client

    try:
        connection_kwargs = {
            "host": redis_settings.REDIS_HOST,
            "port": redis_settings.REDIS_PORT,
            "db": redis_settings.REDIS_DB,
            "password": redis_settings.REDIS_PASSWORD,
            "ssl": redis_settings.REDIS_SSL,
            "decode_responses": redis_settings.REDIS_DECODE_RESPONSES,
            "socket_connect_timeout": redis_settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        }

        # Remove None values
        connection_kwargs = {
            k: v for k, v in connection_kwargs.items() if v is not None
        }

        _redis_client = redis.Redis(**connection_kwargs)

        # Test connection
        await _redis_client.ping()
        logger.info(
            f"Redis connected to {redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}"
        )

    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        _redis_client = None
        raise


async def get_redis_client() -> redis.Redis:
    """Get global Redis client"""
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call initialize_redis() first."
        )
    return _redis_client


async def close_redis():
    """Close global Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


def is_redis_initialized() -> bool:
    """Check if Redis is initialized"""
    return _redis_client is not None
