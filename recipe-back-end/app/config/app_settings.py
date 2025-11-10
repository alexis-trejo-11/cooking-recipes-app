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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def create_application() -> FastAPI:
    """Factory function para crear la aplicación FastAPI"""

    app = FastAPI(
        title="Cooking Recipes API",
        description="An API to manage and retrieve cooking recipes.",
        version="1.0.0",
        debug=settings.DEBUG,
    )

    _configure_exception_handlers(app)

    return app


def _configure_exception_handlers(app: FastAPI):
    """Configurar todos los handlers de excepciones"""

    # Handler global
    GlobalExceptionHandler(app, debug=app.debug)
