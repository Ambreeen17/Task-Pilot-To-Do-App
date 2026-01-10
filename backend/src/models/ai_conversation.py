"""
Phase 3: AI-Assisted Todo - AIConversation Model

Multi-turn conversation session between user and AI assistant.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .ai_message import AIMessage
    from .user import User


class AIConversation(SQLModel, table=True):
    """
    Conversation session tracking user-AI interactions.

    Lifecycle:
    - Created when user starts AI conversation
    - Status: active -> closed/timeout
    - Auto-timeout after 10 minutes of inactivity
    - Soft delete via deleted_at field
    """

    __tablename__ = "ai_conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity_time: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active", max_length=20)
    context_window: int = Field(default=10, ge=1, le=20)
    topic: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    # Relationships
    messages: list["AIMessage"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="ai_conversations")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "status": "active",
                "context_window": 10,
                "topic": "Task creation",
            }
        }
