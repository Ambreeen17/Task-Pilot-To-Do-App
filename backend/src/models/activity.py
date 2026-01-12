from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class AIActivityLog(SQLModel, table=True):
    __tablename__ = "ai_activity_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    action_type: str  # "suggestion", "notification", "auto_action"
    entity_target: str  # e.g. "Task:123"
    reasoning: str  # "Task due in 1h, user inactive"
    status: str  # "pending", "accepted", "rejected", "displayed"
    timestamp: datetime = Field(default_factory=utcnow)
