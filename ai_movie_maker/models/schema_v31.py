from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class VisualPrompt(BaseModel):
    positive: str
    negative: str

class Dialogue(BaseModel):
    text: str
    voice_gender: Literal["Male", "Female"]

class Audio(BaseModel):
    sfx: str
    music_mood: str

class SceneV31(BaseModel):
    scene_id: int
    duration_seconds: int = Field(ge=2, le=4)
    visual_prompt: VisualPrompt
    dialogue: Dialogue
    audio: Audio

class ScriptV31(BaseModel):
    project_title: str
    global_style: dict
    scenes: List[SceneV31] = Field(min_length=3, max_length=5)
