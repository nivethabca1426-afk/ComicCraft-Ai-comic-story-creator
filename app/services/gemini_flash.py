import json

from app.config import get_settings
from app.schemas import PanelOutline, PromptRequest


def generate_outline(request: PromptRequest) -> list[PanelOutline]:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    from google import genai
    from google.genai import types

    prompt = f"""
You are the outline planner for ComicCraft, an AI comic story creator.
Create exactly 5 connected comic panels from the user's idea.

Story prompt: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return ONLY valid JSON in this exact shape:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "short title",
      "scene_description": "visual scene description",
      "image_prompt": "detailed image-generation prompt"
    }}
  ]
}}

Requirements:
- Exactly 5 panels, numbered 1 through 5.
- Maintain the same main character and setting across panels.
- Make the story have a clear beginning, development, climax, and ending.
- The image_prompt must describe composition, character appearance, action, lighting, and the requested art style.
- Do not include markdown fences or commentary outside the JSON.
"""

    # Create and use the client inside the same context.
    # It stays open while generate_content() runs and is
    # automatically closed afterward.
    with genai.Client(api_key=settings.gemini_api_key) as client:
        response = client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )

    try:
        data = json.loads(response.text)

        panels = [
            PanelOutline.model_validate(item)
            for item in data["panels"]
        ]

    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Gemini outline response was not valid JSON: {exc}"
        ) from exc

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} panels; exactly 5 are required."
        )

    return panels