from app.schemas import ComicLayout, StoryPanel


def build_comic_layout(story: list[StoryPanel], image_paths: list[str]) -> list[ComicLayout]:
    if len(story) != len(image_paths):
        raise ValueError("Every story panel must have exactly one generated image.")

    return [
        ComicLayout(
            panel_number=panel.panel_number,
            title=panel.title,
            image_path=image_path,
            scene_description=panel.scene_description,
            caption=panel.caption,
            narration=panel.narration,
            dialogue=panel.dialogue,
            image_prompt=panel.image_prompt,
        )
        for panel, image_path in zip(story, image_paths)
    ]
