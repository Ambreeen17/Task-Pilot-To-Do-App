"""
Phase 3: AI-Assisted Todo - ParsedTaskIntent Model

Structured data extracted from natural language input.
"""

import uuid
from datetime import datetime, date, time
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import JSON


if TYPE_CHECKING:
    from .ai_message import AIMessage
    from .task import Task


class ParsedTaskIntent(SQLModel, table=True):
    """
    AI-parsed task information from user input.

    Confidence Scores:
    - ≥0.9: High confidence (auto-accept)
    - 0.7-0.89: Medium confidence (show in UI, allow edit)
    - <0.7: Low confidence (flag as uncertain, prompt review)

    Workflow:
    1. User sends message with task intent
    2. AI parses and extracts fields
    3. User reviews/edits/confirms
    4. Task created and linked via task_id
    """

    __tablename__ = "parsed_task_intents"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="ai_messages.id", index=True)
    original_text: str = Field()
    extracted_title: Optional[str] = Field(default=None, max_length=200)
    extracted_priority: Optional[str] = Field(default=None)
    extracted_due_date: Optional[date] = None
    extracted_due_time: Optional[time] = None
    confidence_scores: dict[str, float] = Field(sa_column=Column(JSON))
    confirmed: bool = Field(default=False)
    task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
    created_at: datetime = Field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None

    # Relationships
    message: "AIMessage" = Relationship(back_populates="parsed_intent")
    task: Optional["Task"] = Relationship()

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 2,
                "original_text": "finish report by Friday",
                "extracted_title": "Finish report",
                "extracted_priority": "High",
                "extracted_due_date": "2026-01-17",
                "confidence_scores": {
                    "title": 0.95,
                    "priority": 0.75,
                    "due_date": 0.90,
                },
                "confirmed": False,
            }
        }
