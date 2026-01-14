from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid


def utcnow():
    """UTC timestamp"""
    return datetime.utcnow()


class UserPreferences(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)

    # Phase 4 preferences
    autonomy_level: str = Field(default="low")  # "low", "medium", "high"
    enabled_categories: str = Field(default='["reminders", "scheduling"]')  # JSON string
    work_start_hour: int = Field(default=9)
    work_end_hour: int = Field(default=17)

    # Phase 5: Learning consent and controls (GDPR/CCPA compliance)
    learning_enabled: bool = Field(
        default=False,
        description="Opt-in required for behavioral learning (GDPR Article 6)"
    )
    learning_consent_date: Optional[datetime] = Field(
        default=None,
        description="When user consented to learning (audit trail)"
    )
    learning_categories: str = Field(
        default='[]',
        description="Which pattern types user consents to: ['timing', 'priority', 'grouping']"
    )
    learning_paused: bool = Field(
        default=False,
        description="Temporarily pause learning without losing existing patterns"
    )
    pattern_visibility: str = Field(
        default="high",
        description="Confidence threshold for showing patterns: 'low' (0.4), 'medium' (0.6), 'high' (0.75)"
    )
