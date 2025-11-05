from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.sql_session import init_db, close_db
import uvicorn
from app.auth.presentation.auth_controller import router as auth_router

app = FastAPI(
    title="Cooking Recipes API",
    description="An API to manage and retrieve cooking recipes.",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


@app.get("/")
async def home():
    return {"message": "Welcome to the Cooking Recipes API!"}


app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
