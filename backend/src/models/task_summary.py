"""
Phase 3: AI-Assisted Todo - TaskSummary Model

AI-generated summary of tasks over a time period.
"""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class TaskSummary(SQLModel, table=True):
    """
    AI-generated task summary with metrics.

    Period Types:
    - daily: Single day summary
    - weekly: 7-day summary
    - monthly: 30-day summary
    - custom: User-defined date range

    Metrics Include:
    - Total tasks, completed, pending, overdue
    - Completion rate
    - Priority distribution
    - Average completion time
    """

    __tablename__ = "task_summaries"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    period_type: str = Field(max_length=20)
    start_date: date = Field()
    end_date: date = Field()
    metrics: dict = Field(sa_column=Column(JSON))
    summary_text: str = Field()
    generated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "period_type": "weekly",
                "start_date": "2026-01-03",
                "end_date": "2026-01-10",
                "metrics": {
                    "total_tasks": 42,
                    "completed": 30,
                    "pending": 8,
                    "overdue": 4,
                    "completion_rate": 0.71,
                },
                "summary_text": "Great week! You completed 30 tasks with a 71% completion rate.",
            }
        }
