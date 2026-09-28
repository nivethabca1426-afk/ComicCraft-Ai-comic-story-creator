import re
from pathlib import Path
from uuid import uuid4

from PIL import Image

from app.config import BASE_DIR, get_settings

PANELS_DIR = BASE_DIR / "app" / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", prompt.lower()).strip("-")
    return (slug[:55] or "comic-panel") + f"-{uuid4().hex[:8]}.png"


def _generate_hf(prompt: str, output_path: Path) -> None:
    settings = get_settings()
    if not settings.hf_api_key:
        raise RuntimeError("HF_API_KEY is missing. Add your Hugging Face token to .env.")

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        api_key=settings.hf_api_key,
        timeout=180,
    )
    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    image.save(output_path)


def _generate_local(prompt: str, output_path: Path) -> None:
    settings = get_settings()
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local Diffusers backend requires torch and diffusers. Install the optional local requirements."
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(settings.local_image_model, torch_dtype=dtype)
    pipe = pipe.to(device)
    result = pipe(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    result.images[0].save(output_path)


def generate_image(prompt: str) -> str:
    settings = get_settings()
    filename = _safe_name(prompt)
    output_path = PANELS_DIR / filename

    if settings.image_backend.lower() == "local":
        _generate_local(prompt, output_path)
    else:
        _generate_hf(prompt, output_path)

    return f"/static/panels/{filename}"
