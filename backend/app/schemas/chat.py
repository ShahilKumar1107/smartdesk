# chat.py — Data shapes for chat endpoints

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is your return policy?",
                "session_id": "session_123"
            }
        }

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]