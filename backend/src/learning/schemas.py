"""
Learning Schemas - Phase 5

Pydantic schemas for behavioral learning API requests/responses.
All schemas enforce privacy boundaries defined in signal_policy.py

Reference: ADR-001 Privacy-Preserving Behavioral Learning Architecture
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Types of behavioral events that can be captured"""
    TASK_COMPLETED = "task_completed"
    PRIORITY_CHANGED = "priority_changed"
    TASK_GROUPED = "task_grouped"


class BehavioralEventCreate(BaseModel):
    """
    Schema for creating a new behavioral event.

    Privacy Guarantee: Only metadata (timing, frequency, grouping) is captured.
    NO task content, titles, descriptions, or user-defined metadata.
    """
    event_type: EventType
    hour_of_day: int = Field(ge=0, le=23, description="Hour when event occurred (0-23)")
    day_of_week: int = Field(ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    task_type_hash: str = Field(
        min_length=64,
        max_length=64,
        description="SHA-256 hash of generic task type (NOT content)"
    )
    session_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Session ID for grouping related actions"
    )

    @validator('task_type_hash')
    def validate_hash_format(cls, v):
        """Ensure task_type_hash is valid hexadecimal"""
        try:
            int(v, 16)
            return v
        except ValueError:
            raise ValueError("task_type_hash must be valid hexadecimal (SHA-256)")

    class Config:
        schema_extra = {
            "example": {
                "event_type": "task_completed",
                "hour_of_day": 14,
                "day_of_week": 2,
                "task_type_hash": "a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
                "session_id": "sess_abc123"
            }
        }


class BehavioralEventResponse(BaseModel):
    """Response schema for behavioral event"""
    id: int
    user_id: str
    event_type: EventType
    hour_of_day: int
    day_of_week: int
    task_type_hash: str
    session_id: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


class PriorityChangeEvent(BaseModel):
    """
    Schema for priority change behavioral events.

    Captures pattern: from_priority -> to_priority (e.g., "low" -> "high")
    """
    from_priority: str = Field(description="Original priority (low, medium, high)")
    to_priority: str = Field(description="New priority (low, medium, high)")
    hour_of_day: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    session_id: Optional[str] = None

    @validator('from_priority', 'to_priority')
    def validate_priority(cls, v):
        """Ensure priority values are valid"""
        if v not in ["low", "medium", "high"]:
            raise ValueError("Priority must be one of: low, medium, high")
        return v


class LearnedPattern(BaseModel):
    """Base schema for learned behavioral patterns"""
    pattern_type: str
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in pattern (0-1)")
    data_points: int = Field(ge=0, description="Number of events used to learn pattern")
    last_updated: datetime


class PeakHoursPattern(LearnedPattern):
    """User's peak productivity hours pattern"""
    pattern_type: str = "peak_hours"
    peak_hours: Dict[int, float] = Field(
        description="Hour (0-23) -> productivity score (0-1)"
    )
    top_3_hours: List[int] = Field(description="Top 3 most productive hours")


class TaskTimingPattern(LearnedPattern):
    """Task type timing preferences pattern"""
    pattern_type: str = "type_timing"
    type_timing: Dict[str, Dict[int, int]] = Field(
        description="task_type_hash -> {hour -> frequency}"
    )


class PriorityAdjustmentPattern(LearnedPattern):
    """Priority adjustment behavior pattern"""
    pattern_type: str = "priority_adjustment"
    adjustment_flows: Dict[str, Dict[str, int]] = Field(
        description="from_priority -> {to_priority -> frequency}"
    )


class GroupingPattern(LearnedPattern):
    """Task grouping behavior pattern"""
    pattern_type: str = "grouping"
    related_types: Dict[str, List[str]] = Field(
        description="task_type_hash -> [related_task_type_hashes]"
    )


class UserBehaviorProfileResponse(BaseModel):
    """Complete user behavior profile with all learned patterns"""
    user_id: str
    learning_enabled: bool
    data_points_collected: int
    last_learning_date: Optional[datetime]
    model_version: str

    # Learned patterns (empty if learning disabled or insufficient data)
    peak_hours_pattern: Optional[PeakHoursPattern] = None
    task_timing_pattern: Optional[TaskTimingPattern] = None
    priority_pattern: Optional[PriorityAdjustmentPattern] = None
    grouping_pattern: Optional[GroupingPattern] = None

    class Config:
        orm_mode = True


class LearningControlRequest(BaseModel):
    """Request to enable/disable learning or reset data"""
    action: str = Field(description="Action: 'enable', 'disable', 'reset'")

    @validator('action')
    def validate_action(cls, v):
        """Ensure action is valid"""
        if v not in ["enable", "disable", "reset"]:
            raise ValueError("Action must be one of: enable, disable, reset")
        return v


class LearningStatusResponse(BaseModel):
    """Current learning status for user"""
    learning_enabled: bool
    data_points_collected: int
    days_since_enabled: Optional[int] = None
    patterns_ready: bool = Field(
        description="True if sufficient data for pattern detection (≥20 events)"
    )
    next_learning_job: Optional[datetime] = Field(
        description="When next batch learning job will run"
    )


class PrivacySummaryResponse(BaseModel):
    """Privacy policy summary for transparency"""
    learnable_signals: List[str] = Field(
        description="Signals that ARE learned (privacy-safe metadata)"
    )
    forbidden_signals: List[str] = Field(
        description="Signals that are NEVER learned (privacy-protected)"
    )
    privacy_guarantees: List[str] = Field(
        default=[
            "No task content, titles, or descriptions stored",
            "Only timing, frequency, and grouping patterns learned",
            "All learning is opt-in and reversible",
            "Complete data deletion available at any time",
            "GDPR Article 15 & 17 compliant"
        ]
    )
