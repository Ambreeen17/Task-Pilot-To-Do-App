"""
Phase 3: AI-Assisted Todo - AIInsight Model

Pattern-based recommendation or productivity insight.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class AIInsight(SQLModel, table=True):
    """
    AI-detected pattern or recommendation.

    Insight Types:
    - overdue_pattern: Consistently has overdue tasks
    - productivity_trend: Completion rate changing
    - priority_imbalance: Too many High priority tasks
    - completion_streak: Completing tasks consistently
    - workload_warning: Too many tasks due soon
    - time_management: Tasks taking longer than expected
    - recurring_task: Detected repeating pattern
    - other: Miscellaneous insights

    Lifecycle:
    - Created by insight generator
    - Displayed to user
    - User can dismiss with optional reason
    """

    __tablename__ = "ai_insights"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    insight_type: str = Field(max_length=50)
    title: str = Field(max_length=200)
    description: str = Field()
    supporting_data: dict = Field(sa_column=Column(JSON))
    priority: str = Field(default="Medium", max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
    dismissed_at: Optional[datetime] = None
    dismissed_reason: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "insight_type": "productivity_trend",
                "title": "Productivity improving!",
                "description": "Your completion rate has increased by 21% in the last 14 days.",
                "supporting_data": {
                    "period": "last_14_days",
                    "completion_rate_current": 0.85,
                    "completion_rate_previous": 0.70,
                    "trend": "improving",
                },
                "priority": "Medium",
            }
        }
