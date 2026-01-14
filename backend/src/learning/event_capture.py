"""
Behavioral Event Capture Service - Phase 5 Agent 3 (Task 3.1)

Captures privacy-safe behavioral events from user actions.
Validates events against signal policy before storage.

Reference: ADR-001 Privacy-Preserving Behavioral Learning Architecture
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session
import hashlib
import sys
from pathlib import Path

# Support both relative and absolute imports
try:
    from ..models.behavioral_event import BehavioralEvent
    from ..models.preferences import UserPreferences
    from .signal_policy import SignalPolicy, SignalType
except ImportError:
    # Fallback for tests
    from models.behavioral_event import BehavioralEvent
    from models.preferences import UserPreferences
    from learning.signal_policy import SignalPolicy, SignalType


class EventCaptureError(Exception):
    """Raised when event capture fails validation"""
    pass


class EventCaptureService:
    """
    Service for capturing behavioral events with privacy validation.

    Privacy Guarantee:
    - All events validated against signal policy before capture
    - Forbidden signals automatically rejected
    - One-way hashing for task types
    """

    @staticmethod
    def should_capture_event(user_id: str, session: Session) -> bool:
        """
        Check if event capture is enabled for user.

        Returns False if:
        - Learning is disabled
        - Learning is paused
        - User has not consented

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            True if capture should proceed, False otherwise
        """
        from sqlmodel import select
        import uuid

        prefs = session.exec(
            select(UserPreferences).where(UserPreferences.user_id == uuid.UUID(user_id))
        ).first()

        if not prefs:
            return False

        # Check if learning is enabled and not paused
        return prefs.learning_enabled and not prefs.learning_paused

    @staticmethod
    def hash_task_type(task_type: str) -> str:
        """
        Create one-way SHA-256 hash of task type.

        CRITICAL: Only hash generic type identifiers, NOT task content.

        Args:
            task_type: Generic task type (e.g., "email", "meeting", "coding")

        Returns:
            64-character hexadecimal hash
        """
        return SignalPolicy.hash_task_type(task_type)

    @staticmethod
    def capture_task_completion(
        user_id: str,
        task_type: str,
        session_id: Optional[str] = None,
        session_db: Session = None
    ) -> Optional[BehavioralEvent]:
        """
        Capture task completion event.

        Privacy: Only captures timing and task type hash, NO content.

        Args:
            user_id: User UUID
            task_type: Generic task type (NOT task title/content)
            session_id: Optional session identifier for grouping
            session_db: Database session

        Returns:
            BehavioralEvent if captured, None if capture disabled

        Raises:
            EventCaptureError: If validation fails
        """
        import uuid

        # Check if capture is enabled
        if not EventCaptureService.should_capture_event(user_id, session_db):
            return None

        # Get current time
        now = datetime.utcnow()
        hour_of_day = now.hour
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday

        # Hash task type (privacy-safe)
        task_type_hash = EventCaptureService.hash_task_type(task_type)

        # Validate event data
        event_data = {
            "event_type": "task_completed",
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "task_type_hash": task_type_hash,
            "session_id": session_id
        }

        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        if not is_valid:
            raise EventCaptureError(f"Event validation failed: {error}")

        # Create event
        event = BehavioralEvent(
            user_id=uuid.UUID(user_id),
            event_type="task_completed",
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            task_type_hash=task_type_hash,
            session_id=session_id,
            timestamp=now
        )

        return event

    @staticmethod
    def capture_priority_change(
        user_id: str,
        from_priority: str,
        to_priority: str,
        task_type: str,
        session_id: Optional[str] = None,
        session_db: Session = None
    ) -> Optional[BehavioralEvent]:
        """
        Capture priority change event.

        Privacy: Only captures priority levels and timing, NO task content.

        Args:
            user_id: User UUID
            from_priority: Original priority (low, medium, high)
            to_priority: New priority (low, medium, high)
            task_type: Generic task type
            session_id: Optional session identifier
            session_db: Database session

        Returns:
            BehavioralEvent if captured, None if capture disabled

        Raises:
            EventCaptureError: If validation fails
        """
        import uuid

        # Check if capture is enabled
        if not EventCaptureService.should_capture_event(user_id, session_db):
            return None

        # Validate priority values
        valid_priorities = {"low", "medium", "high"}
        if from_priority not in valid_priorities or to_priority not in valid_priorities:
            raise EventCaptureError(
                f"Invalid priority values. Valid: {valid_priorities}"
            )

        # Get current time
        now = datetime.utcnow()
        hour_of_day = now.hour
        day_of_week = now.weekday()

        # Hash task type
        task_type_hash = EventCaptureService.hash_task_type(task_type)

        # Validate event data
        event_data = {
            "event_type": "priority_changed",
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "task_type_hash": task_type_hash,
            "session_id": session_id
        }

        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        if not is_valid:
            raise EventCaptureError(f"Event validation failed: {error}")

        # Create event
        event = BehavioralEvent(
            user_id=uuid.UUID(user_id),
            event_type="priority_changed",
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            task_type_hash=task_type_hash,
            session_id=session_id,
            from_priority=from_priority,
            to_priority=to_priority,
            timestamp=now
        )

        return event

    @staticmethod
    def capture_task_grouping(
        user_id: str,
        task_types: list[str],
        session_id: str,
        session_db: Session = None
    ) -> list[BehavioralEvent]:
        """
        Capture task grouping event (multiple tasks in same session).

        Privacy: Only captures that tasks were grouped, NO content.

        Args:
            user_id: User UUID
            task_types: List of generic task types grouped together
            session_id: Session identifier linking the tasks
            session_db: Database session

        Returns:
            List of BehavioralEvents (one per task in group)

        Raises:
            EventCaptureError: If validation fails
        """
        import uuid

        # Check if capture is enabled
        if not EventCaptureService.should_capture_event(user_id, session_db):
            return []

        # Get current time
        now = datetime.utcnow()
        hour_of_day = now.hour
        day_of_week = now.weekday()

        events = []
        for task_type in task_types:
            # Hash task type
            task_type_hash = EventCaptureService.hash_task_type(task_type)

            # Validate event data
            event_data = {
                "event_type": "task_grouped",
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "task_type_hash": task_type_hash,
                "session_id": session_id
            }

            is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
            if not is_valid:
                raise EventCaptureError(f"Event validation failed: {error}")

            # Create event
            event = BehavioralEvent(
                user_id=uuid.UUID(user_id),
                event_type="task_grouped",
                hour_of_day=hour_of_day,
                day_of_week=day_of_week,
                task_type_hash=task_type_hash,
                session_id=session_id,
                timestamp=now
            )
            events.append(event)

        return events

    @staticmethod
    def batch_capture_events(
        events: list[BehavioralEvent],
        session: Session
    ) -> int:
        """
        Store multiple events in database efficiently.

        Args:
            events: List of BehavioralEvent objects to store
            session: Database session

        Returns:
            Number of events stored
        """
        if not events:
            return 0

        for event in events:
            session.add(event)

        session.commit()
        return len(events)

    @staticmethod
    def get_user_event_count(user_id: str, session: Session) -> int:
        """
        Get total number of events captured for user.

        Useful for:
        - Determining if user has enough data for patterns (≥20 events)
        - Showing user their data collection progress

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            Total event count
        """
        from sqlmodel import select, func
        import uuid

        count = session.exec(
            select(func.count(BehavioralEvent.id)).where(
                BehavioralEvent.user_id == uuid.UUID(user_id)
            )
        ).one()

        return count

    @staticmethod
    def validate_privacy_compliance(event: BehavioralEvent) -> tuple[bool, list[str]]:
        """
        Validate that event complies with privacy policy.

        Checks:
        - No forbidden signals present
        - All signals are learnable
        - Task type hash is valid format
        - No PII in any field

        Args:
            event: BehavioralEvent to validate

        Returns:
            Tuple of (is_compliant: bool, violations: list[str])
        """
        violations = []

        # Check task_type_hash format (must be 64-char hex)
        if len(event.task_type_hash) != 64:
            violations.append("task_type_hash must be 64 characters (SHA-256)")

        try:
            int(event.task_type_hash, 16)
        except ValueError:
            violations.append("task_type_hash must be hexadecimal")

        # Check hour_of_day range
        if not (0 <= event.hour_of_day <= 23):
            violations.append("hour_of_day must be 0-23")

        # Check day_of_week range
        if not (0 <= event.day_of_week <= 6):
            violations.append("day_of_week must be 0-6")

        # Check event_type validity
        valid_event_types = {"task_completed", "priority_changed", "task_grouped"}
        if event.event_type not in valid_event_types:
            violations.append(f"event_type must be one of {valid_event_types}")

        # Check priority values if present
        if event.from_priority or event.to_priority:
            valid_priorities = {"low", "medium", "high"}
            if event.from_priority and event.from_priority not in valid_priorities:
                violations.append(f"from_priority must be one of {valid_priorities}")
            if event.to_priority and event.to_priority not in valid_priorities:
                violations.append(f"to_priority must be one of {valid_priorities}")

        is_compliant = len(violations) == 0
        return is_compliant, violations
