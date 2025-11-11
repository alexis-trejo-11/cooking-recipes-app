from pydantic_settings import BaseSettings
from fastapi import FastAPI
from app.config.global_exception_handler import GlobalExceptionHandler


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_TIMEOUT: float = 5.0
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 30
    DEBUG: bool = False

    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "default"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
