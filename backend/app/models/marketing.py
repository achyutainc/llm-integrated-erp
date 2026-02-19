from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, date

class SocialMediaPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str # "facebook", "instagram", "google"
    content: str
    image_url: Optional[str] = None
    scheduled_date: date = Field(default_factory=date.today)
    status: str = Field(default="draft") # draft, scheduled, posted

    # AI Metadata
    ai_generated: bool = Field(default=True)
    prompt_used: Optional[str] = None
