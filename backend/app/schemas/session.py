from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SessionBase(BaseModel):
    title: Optional[str] = None
    source_language: str
    target_language: str
    metadata: Optional[Dict[str, Any]] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    ended_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(SessionBase):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

