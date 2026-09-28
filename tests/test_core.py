from app.schemas import PanelOutline, PromptRequest, StoryPanel
from app.services.layout_builder import build_comic_layout


def test_prompt_request_validation():
    request = PromptRequest(
        story_prompt="A fox explores a forest.",
        character_name="Luna",
        setting="Forest",
        tone="Funny",
        art_style="Comic book",
    )
    assert request.character_name == "Luna"


def test_layout_builder_matches_images():
    story = [
        StoryPanel(
            panel_number=1,
            title="Start",
            scene_description="A forest path.",
            caption="Morning.",
            narration="Luna walks forward.",
            dialogue="Hello!",
            image_prompt="Comic fox in forest",
        )
    ]
    layout = build_comic_layout(story, ["/static/panels/test.png"])
    assert layout[0].image_path == "/static/panels/test.png"
    assert layout[0].panel_number == 1
