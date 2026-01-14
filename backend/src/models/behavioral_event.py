"""
Behavioral Event Model - Phase 5

Captures privacy-safe behavioral metadata for pattern learning.
NO task content, titles, descriptions, or PII is stored.

Reference: ADR-001 Privacy-Preserving Behavioral Learning Architecture
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


def utcnow():
    """UTC timestamp for event recording"""
    return datetime.utcnow()


class BehavioralEvent(SQLModel, table=True):
    """
    Privacy-safe behavioral event capturing ONLY metadata.

    Privacy Guarantee:
    - Only timing (hour, day), frequency (event type), and grouping (session) stored
    - NO task content, titles, descriptions, categories, tags, or PII
    - task_type_hash is ONE-WAY hash (cannot reconstruct original)
    """
    __tablename__ = "behavioral_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Event classification
    event_type: str = Field(
        index=True,
        description="Type: task_completed, priority_changed, task_grouped"
    )

    # Timing metadata (privacy-safe)
    hour_of_day: int = Field(
        ge=0, le=23,
        description="Hour when action occurred (0-23)"
    )
    day_of_week: int = Field(
        ge=0, le=6,
        description="Day of week (0=Monday, 6=Sunday)"
    )

    # Task type (privacy-safe one-way hash)
    task_type_hash: str = Field(
        max_length=64,
        description="SHA-256 hash of generic task type (NOT content)"
    )

    # Session grouping (privacy-safe)
    session_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Session identifier for grouping related actions"
    )

    # Priority change tracking (for priority_changed events)
    from_priority: Optional[str] = Field(
        default=None,
        description="Original priority (low, medium, high)"
    )
    to_priority: Optional[str] = Field(
        default=None,
        description="New priority (low, medium, high)"
    )

    # Metadata
    timestamp: datetime = Field(default_factory=utcnow, index=True)
    created_at: datetime = Field(default_factory=utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "task_completed",
                "hour_of_day": 14,
                "day_of_week": 2,
                "task_type_hash": "a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
                "session_id": "sess_abc123",
                "from_priority": None,
                "to_priority": None
            }
        }


class UserBehaviorProfile(SQLModel, table=True):
    """
    Aggregated behavioral patterns learned from BehavioralEvent data.

    Stores statistical summaries, NOT raw events.
    All patterns are JSON-encoded for flexibility.
    """
    __tablename__ = "user_behavior_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)

    # Learned patterns (JSON-encoded)
    peak_hours: str = Field(
        default="{}",
        description="Time-of-day preferences: {hour: frequency_score}"
    )
    type_timing_patterns: str = Field(
        default="{}",
        description="Task type patterns: {type_hash: {hour: frequency}}"
    )
    priority_adjustment_patterns: str = Field(
        default="{}",
        description="Priority change patterns: {from_priority: {to_priority: frequency}}"
    )
    grouping_patterns: str = Field(
        default="{}",
        description="Session grouping patterns: {type_hash: [related_type_hashes]}"
    )

    # Learning metadata
    data_points_collected: int = Field(default=0, ge=0)
    last_learning_date: Optional[datetime] = Field(default=None)
    model_version: str = Field(default="1.0")

    # User control
    learning_enabled: bool = Field(
        default=False,
        description="User must explicitly opt-in to learning"
    )
    learning_paused: bool = Field(
        default=False,
        description="User can temporarily pause learning"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "peak_hours": '{"9": 0.75, "14": 0.90, "16": 0.82}',
                "type_timing_patterns": '{"abc123": {"9": 10, "14": 15}}',
                "priority_adjustment_patterns": '{"low": {"high": 5, "medium": 3}}',
                "grouping_patterns": '{"abc123": ["def456", "ghi789"]}',
                "data_points_collected": 156,
                "learning_enabled": True,
                "learning_paused": False
            }
        }
