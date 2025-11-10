from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.sql_session import init_db, close_db
import uvicorn
from app.modules.auth.presentation.auth_controller import router as auth_router
from app.modules.recipe.presentation.controller import router as recipe_router
from app.config.app_settings import create_application
from app.config.logging_config import setup_logging

setup_logging()

app = create_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


@app.get("/")
async def home():
    return {"message": "Welcome to the Cooking Recipes API!"}


app.include_router(auth_router)
app.include_router(recipe_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_config=None)
