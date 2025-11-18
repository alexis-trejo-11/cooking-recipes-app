from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_TIMEOUT: float = 5.0
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 90  # 3 months

    DEBUG: bool = False

    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "default"

    SSL_ENABLED: bool = False
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    SERVER_PORT: int = 8080
    SSL_PORT: int = 8443

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
