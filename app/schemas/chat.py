from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    """Schema for an incoming chat message."""
    input: str
    history: List[Dict] = []

class ChatResponse(BaseModel):
    """Schema for a non-streaming chat response."""
    response: str
    history: List[Dict]