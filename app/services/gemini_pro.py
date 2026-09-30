import json

from app.config import get_settings
from app.schemas import PanelOutline, PromptRequest, StoryPanel


def generate_story(
    request: PromptRequest,
    outline: list[PanelOutline],
) -> list[StoryPanel]:

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    from google import genai
    from google.genai import types

    outline_json = json.dumps(
        [panel.model_dump() for panel in outline],
        ensure_ascii=False,
    )

    prompt = f"""
You are the senior comic writer for ComicCraft.
Expand this 5-panel outline into polished comic narration, captions, and dialogue.

User preferences:
Story prompt: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_json}

Return ONLY valid JSON in this exact shape:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "title",
      "scene_description": "short atmospheric description",
      "caption": "brief ambient caption",
      "narration": "comic narration describing action and emotion",
      "dialogue": "short character dialogue, or empty string",
      "image_prompt": "final detailed image prompt"
    }}
  ]
}}

Requirements:
- Exactly 5 panels and preserve panel order.
- Keep character names and continuity consistent.
- Make dialogue natural and concise enough for a comic panel.
- Keep the tone exactly aligned with the requested tone.
- Keep the visual prompts suitable for a comic illustration model.
- Do not include markdown fences or commentary outside the JSON.
"""

    # Keep the Gemini client open while the request is running.
    with genai.Client(api_key=settings.gemini_api_key) as client:
        response = client.models.generate_content(
            model=settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                response_mime_type="application/json",
            ),
        )

    try:
        data = json.loads(response.text)

        panels = [
            StoryPanel.model_validate(item)
            for item in data["panels"]
        ]

    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Gemini story response was not valid JSON: {exc}"
        ) from exc

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} story panels; exactly 5 are required."
        )

    return panels