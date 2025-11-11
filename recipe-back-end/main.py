from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config.sql_session import init_db, close_db
import uvicorn
from app.modules.auth.presentation.auth_controller import router as auth_router
from app.modules.recipe.presentation.controller import router as recipe_router
from app.config.logging_config import setup_logging
from app.config.rate_limiter import rate_limit, rate_limit_manager
from app.config.app_settings import settings
from app.config.global_exception_handler import (
    GlobalExceptionHandler,
    RateLimitException,
)


setup_logging()

app_stats = {"total_requests": 0, "blocked_requests": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Cooking Recipes API",
    description="An API to manage and retrieve cooking recipes.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

GlobalExceptionHandler(app, debug=settings.DEBUG)


async def rate_limiter_dependency(request: Request):
    if not settings.RATE_LIMIT_ENABLED:
        print("🔓 Rate limiting disabled")
        return True

    endpoint = "unknown"
    try:
        endpoint_func = request.scope.get("endpoint")
        if endpoint_func:
            endpoint = f"{endpoint_func.__module__}.{endpoint_func.__name__}"
        else:
            endpoint = request.url.path
        result = await rate_limit_manager.check_rate_limit(request, endpoint)
        return result
    except RateLimitException as e:
        if e.status_code == 429:
            print(f"Rate limit exceeded for: {endpoint}")
        raise e
    except Exception as e:
        print(f"Error en rate limiter: {e}")
        return True


@app.middleware("http")
async def add_stats_middleware(request: Request, call_next):
    app_stats["total_requests"] += 1
    try:
        response = await call_next(request)
        return response
    except HTTPException as exc:
        if exc.status_code == 429:
            app_stats["blocked_requests"] += 1
        raise exc


@app.get("/")
async def home():
    return {"message": "Welcome to the Cooking Recipes API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth_router, dependencies=[Depends(rate_limiter_dependency)])
app.include_router(recipe_router, dependencies=[Depends(rate_limiter_dependency)])


# Endpoints de administración (sin rate limiting)
@app.get("/admin/rate-limit-status")
async def rate_limit_status():
    return {
        "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
        "app_stats": app_stats,
        "active_limits": len(rate_limit_manager.request_counts),
        "configured_endpoints": len(rate_limit_manager.endpoint_configs),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_config=None)
