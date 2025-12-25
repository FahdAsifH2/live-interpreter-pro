from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TranscriptBase(BaseModel):
    original_text: str
    translated_text: Optional[str] = None
    source_language: str
    target_language: str
    timestamp: float
    confidence: Optional[float] = None


class TranscriptCreate(TranscriptBase):
    session_id: int


class TranscriptResponse(TranscriptBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

