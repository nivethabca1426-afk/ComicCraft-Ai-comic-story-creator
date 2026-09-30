from pathlib import Path

from app.config import BASE_DIR, get_settings

PANELS_DIR = BASE_DIR / "app" / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str, panel_number: int = 1) -> str:
    settings = get_settings()
    token = settings.hf_token or settings.hf_api_key
    if not token:
        raise RuntimeError(
            "HF_TOKEN is missing. Set HF_TOKEN or the legacy HF_API_KEY in .env."
        )

    from huggingface_hub import InferenceClient

    output_path = PANELS_DIR / f"panel_{panel_number}.png"
    try:
        client = InferenceClient(
            provider="auto",
            token=token,
            timeout=180,
        )
        image = client.text_to_image(
            prompt=prompt,
            model=settings.hf_image_model,
            width=settings.image_width,
            height=settings.image_height,
        )
    except Exception as exc:
        message = str(exc).replace(token, "[REDACTED]")
        raise RuntimeError(message) from None

    image.save(output_path, format="PNG")

    return f"/static/panels/panel_{panel_number}.png"
