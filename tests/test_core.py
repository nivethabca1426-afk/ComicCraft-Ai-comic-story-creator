from app.schemas import PanelOutline, PromptRequest, StoryPanel
from app.services.layout_builder import build_comic_layout
from app.services.local_story import generate_local_story


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


def test_local_story_generates_five_prompt_aware_panels():
    request = PromptRequest(
        story_prompt="A young fox discovers an injured owl during a storm and helps it find its family before sunrise.",
        character_name="Luna",
        setting="Forest",
        tone="Hopeful",
        art_style="Comic book",
    )

    panels = generate_local_story(request)

    assert [panel.panel_number for panel in panels] == [1, 2, 3, 4, 5]
    for panel in panels:
        assert panel.title
        assert panel.scene_description
        assert panel.image_prompt
        assert panel.narration
        assert panel.dialogue
        assert request.story_prompt in panel.image_prompt
    assert "Luna" in panels[3].scene_description
    assert "helps it find its family before sunrise" in panels[3].scene_description
