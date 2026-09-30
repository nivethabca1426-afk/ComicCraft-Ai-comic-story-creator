import re

from app.schemas import PromptRequest, StoryPanel


def _split_story_goal(prompt: str) -> tuple[str, str]:
    parts = re.split(r"\s+(?:and|but|then)\s+", prompt.strip(), maxsplit=1, flags=re.IGNORECASE)
    opening = parts[0].rstrip(" .!?")
    goal = parts[1].rstrip(" .!?") if len(parts) > 1 else ""
    return opening, goal


def generate_local_story(request: PromptRequest) -> list[StoryPanel]:
    opening, goal = _split_story_goal(request.story_prompt)
    character = request.character_name
    setting = request.setting
    tone = request.tone.lower()
    action = f"{character} {goal[0].lower() + goal[1:]}" if goal else ""

    beats = [
        (
            "The Discovery",
            f"In {setting}, {character} encounters the opening situation: {opening}.",
            f"The day changes in an instant as {character} meets the first challenge.",
            "What happened?",
            "A wide establishing view introduces the setting and the beginning of the adventure.",
        ),
        (
            "The Stakes",
            f"A closer look reveals why the story matters. {character} considers the stakes in: {request.story_prompt}",
            f"There is more at stake than first appeared, and {character} decides to act.",
            "I have to do something.",
            "A closer, expressive view shows the important discovery and the character's reaction.",
        ),
        (
            "Against the Odds",
            f"An obstacle in {setting} makes the goal harder to reach, testing {character}'s resolve.",
            "The way forward grows difficult, but giving up is not an option.",
            "There's still a way.",
            "A dynamic scene emphasizes the obstacle, urgency, and distance still to cover.",
        ),
        (
            "A Brave Plan",
            f"{action.capitalize()}." if action else f"{character} takes a decisive step toward the goal in the story prompt.",
            f"At last, {character} turns concern into a clear and determined action.",
            "Stay with me.",
            "An energetic action scene shows the character making meaningful progress toward the goal.",
        ),
        (
            "A Hopeful Ending",
            (
                f"The effort succeeds: {action}. The story reaches a {tone} resolution."
                if action
                else f"The central goal is resolved in a {tone} ending for {character}."
            ),
            f"The effort pays off, bringing {character}'s adventure to a {tone} close.",
            "We made it.",
            "A warm final scene resolves the story and shows the characters at peace.",
        ),
    ]

    panels = []
    for panel_number, (title, scene, narration, dialogue, visual_focus) in enumerate(beats, start=1):
        image_prompt = (
            f"{request.art_style} comic illustration, panel {panel_number} of a five-panel sequence. "
            f"{visual_focus} Main character: {character}. Setting: {setting}. "
            f"Story premise: {request.story_prompt}. Keep character appearance consistent across panels."
        )
        panels.append(
            StoryPanel(
                panel_number=panel_number,
                title=title,
                scene_description=scene,
                caption=title,
                narration=narration,
                dialogue=dialogue,
                image_prompt=image_prompt,
            )
        )

    return panels