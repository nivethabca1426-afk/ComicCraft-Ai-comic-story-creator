from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="AI Comic Story Creator using Gemini and Stable Diffusion/Hugging Face",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
