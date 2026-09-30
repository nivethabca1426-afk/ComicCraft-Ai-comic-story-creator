from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    gemini_api_key: str = ""
    hf_token: str = ""
    hf_api_key: str = ""
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    image_backend: str = "hf"
    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    image_width: int = 768
    image_height: int = 512
    image_steps: int = 25
    image_guidance: float = 7.5

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
