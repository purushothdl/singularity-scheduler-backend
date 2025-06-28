from pydantic import BaseModel
from typing import List, Optional

class Event(BaseModel):
    """Schema for representing a calendar event to the agent and client."""
    google_event_id: Optional[str] = None
    title: str
    start_time: str
    end_time: str
    attendees: List[str] = []