from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Cooking Recipes API",
    description="An API to manage and retrieve cooking recipes.",
    version="1.0.0",
)


@app.get("/")
async def home():
    return {"message": "Welcome to the Cooking Recipes API!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
