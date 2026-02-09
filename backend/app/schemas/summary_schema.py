from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SummaryStyle(str, Enum):
    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET = "bullet_points"
    CUSTOM = "custom"

class SummaryRequest(BaseModel):
    text: str
    style: SummaryStyle = SummaryStyle.BRIEF
    custom_prompt: Optional[str] = None  # For custom style

class SummaryResponse(BaseModel):
    summary: str
    style: str
    word_count: int
