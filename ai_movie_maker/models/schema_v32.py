from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional

class VisualPrompt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    positive: str
    negative: str

class Dialogue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    voice_gender: Literal["Male", "Female"]

class Audio(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sfx: str
    music_mood: str

class Overlay(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    start_sec: int = Field(ge=0)
    end_sec: int = Field(ge=0)
    position: Literal["top", "center", "bottom"]

class ProductShot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    show_product: bool
    what_to_show: str

class SceneV32(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scene_id: int
    duration_seconds: int = Field(ge=2, le=4)
    visual_prompt: VisualPrompt
    camera: str
    on_screen_text: str
    dialogue: Dialogue
    audio: Audio
    overlays: List[Overlay] = []
    product_shot: ProductShot

class Campaign(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: Literal["TikTok", "Reels", "Shorts"]
    campaign_type: Literal["UGC Review", "Unboxing", "Before-After", "Mini-drama", "Explainer", "Testimonial"]
    product_name: str
    product_category: str
    usp_list: List[str] = Field(min_length=3, max_length=3)
    offer: str
    cta_text: str
    brand_voice: str
    must_avoid: List[str] = []

class ScriptV32(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_title: str
    campaign: Campaign
    global_style: dict
    scenes: List[SceneV32] = Field(min_length=3, max_length=5)
