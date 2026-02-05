"""
Phase 3: AI-Assisted Todo - UserContext Model

Current conversation state for active users (hybrid storage).

Note: This model represents the database backup. Active contexts are kept
in-memory by the ContextManager and synced periodically.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class UserContext(SQLModel, table=True):
    """
    User's conversation context (database backup).

    Storage Strategy:
    - Active contexts kept in-memory (ContextManager)
    - Timeout after 10 minutes of inactivity
    - Persist to database on timeout or explicit close
    - Load from database on conversation resume

    Context Window:
    - Last 10 messages kept in memory
    - Last 50 task references tracked
    """

    __tablename__ = "user_contexts"

    user_id: uuid.UUID = Field(primary_key=True, foreign_key="users.id")
    active_conversation_id: Optional[int] = Field(
        default=None, foreign_key="ai_conversations.id"
    )
    referenced_task_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    last_topic: Optional[str] = Field(default=None, max_length=200)
    last_updated: datetime = Field(default_factory=datetime.now)
    context_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "active_conversation_id": 5,
                "referenced_task_ids": [12, 15, 18],
                "last_topic": "Creating weekly tasks",
                "last_updated": "2026-01-10T14:30:00",
            }
        }
