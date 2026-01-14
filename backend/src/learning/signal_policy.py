"""
Learning Signal Policy - Phase 5 Agent 1

Defines what signals can be learned (privacy-safe) and what cannot be learned (forbidden).
Implements validation logic to ensure no privacy violations occur during data collection.

Reference: ADR-001 Privacy-Preserving Behavioral Learning Architecture
"""

from typing import Dict, List, Set, Any
from enum import Enum
from pydantic import BaseModel, Field
import hashlib


class SignalType(str, Enum):
    """Enumeration of learnable signal types"""
    HOUR_OF_DAY = "hour_of_day"
    DAY_OF_WEEK = "day_of_week"
    TASK_TYPE_HASH = "task_type_hash"
    SESSION_ID = "session_id"
    EVENT_TYPE = "event_type"
    PRIORITY_CHANGE = "priority_change"


class ForbiddenSignalType(str, Enum):
    """Enumeration of explicitly forbidden signals (privacy violations)"""
    TASK_TITLE = "task_title"
    TASK_DESCRIPTION = "task_description"
    TASK_NOTES = "task_notes"
    USER_CATEGORY = "user_category"
    USER_TAG = "user_tag"
    ATTACHMENT_CONTENT = "attachment_content"
    USER_NAME = "user_name"
    USER_EMAIL = "user_email"
    TASK_METADATA = "task_metadata"


class LearnableSignal(BaseModel):
    """Specification of a learnable signal with privacy validation"""
    signal_type: SignalType
    description: str
    data_type: str  # "int", "str", "enum"
    validation_rule: str
    privacy_safe: bool = True
    examples: List[str] = Field(default_factory=list)


class SignalPolicy:
    """
    Central policy for learnable vs forbidden signals.

    Privacy Principle: Only behavioral metadata (timing, frequency, grouping)
    can be learned. No task content or user-identifiable information.
    """

    # Approved learnable signals (privacy-safe)
    LEARNABLE_SIGNALS: Dict[SignalType, LearnableSignal] = {
        SignalType.HOUR_OF_DAY: LearnableSignal(
            signal_type=SignalType.HOUR_OF_DAY,
            description="Hour of day when action occurred (0-23)",
            data_type="int",
            validation_rule="0 <= value <= 23",
            privacy_safe=True,
            examples=["9", "14", "22"]
        ),
        SignalType.DAY_OF_WEEK: LearnableSignal(
            signal_type=SignalType.DAY_OF_WEEK,
            description="Day of week when action occurred (0=Monday, 6=Sunday)",
            data_type="int",
            validation_rule="0 <= value <= 6",
            privacy_safe=True,
            examples=["0", "3", "6"]
        ),
        SignalType.TASK_TYPE_HASH: LearnableSignal(
            signal_type=SignalType.TASK_TYPE_HASH,
            description="One-way SHA-256 hash of task type (NOT content)",
            data_type="str",
            validation_rule="len(value) == 64 and is_hex",
            privacy_safe=True,
            examples=["a3f4b2c1...", "9e8d7f6a..."]
        ),
        SignalType.SESSION_ID: LearnableSignal(
            signal_type=SignalType.SESSION_ID,
            description="Session identifier for grouping related actions",
            data_type="str",
            validation_rule="len(value) <= 64",
            privacy_safe=True,
            examples=["sess_abc123", "sess_xyz789"]
        ),
        SignalType.EVENT_TYPE: LearnableSignal(
            signal_type=SignalType.EVENT_TYPE,
            description="Type of behavioral event",
            data_type="enum",
            validation_rule="value in ['task_completed', 'priority_changed', 'task_grouped']",
            privacy_safe=True,
            examples=["task_completed", "priority_changed"]
        ),
        SignalType.PRIORITY_CHANGE: LearnableSignal(
            signal_type=SignalType.PRIORITY_CHANGE,
            description="Priority change pattern (from -> to)",
            data_type="str",
            validation_rule="format: 'low->high', 'medium->high', etc.",
            privacy_safe=True,
            examples=["low->medium", "medium->high", "high->medium"]
        ),
    }

    # Explicitly forbidden signals (privacy violations)
    FORBIDDEN_SIGNALS: Set[ForbiddenSignalType] = {
        ForbiddenSignalType.TASK_TITLE,
        ForbiddenSignalType.TASK_DESCRIPTION,
        ForbiddenSignalType.TASK_NOTES,
        ForbiddenSignalType.USER_CATEGORY,
        ForbiddenSignalType.USER_TAG,
        ForbiddenSignalType.ATTACHMENT_CONTENT,
        ForbiddenSignalType.USER_NAME,
        ForbiddenSignalType.USER_EMAIL,
        ForbiddenSignalType.TASK_METADATA,
    }

    @classmethod
    def is_signal_learnable(cls, signal_type: str) -> bool:
        """Check if a signal type is approved for learning"""
        try:
            sig = SignalType(signal_type)
            return sig in cls.LEARNABLE_SIGNALS
        except ValueError:
            return False

    @classmethod
    def is_signal_forbidden(cls, signal_type: str) -> bool:
        """Check if a signal type is explicitly forbidden"""
        try:
            sig = ForbiddenSignalType(signal_type)
            return sig in cls.FORBIDDEN_SIGNALS
        except ValueError:
            return False

    @classmethod
    def validate_signal_data(cls, signal_type: SignalType, value: Any) -> bool:
        """
        Validate that signal data meets privacy and format requirements.

        Args:
            signal_type: Type of signal being validated
            value: Signal value to validate

        Returns:
            True if valid and privacy-safe, False otherwise
        """
        if signal_type not in cls.LEARNABLE_SIGNALS:
            return False

        signal_spec = cls.LEARNABLE_SIGNALS[signal_type]

        # Type validation
        if signal_spec.data_type == "int":
            if not isinstance(value, int):
                return False
        elif signal_spec.data_type == "str":
            if not isinstance(value, str):
                return False

        # Range/format validation
        if signal_type == SignalType.HOUR_OF_DAY:
            return 0 <= value <= 23
        elif signal_type == SignalType.DAY_OF_WEEK:
            return 0 <= value <= 6
        elif signal_type == SignalType.TASK_TYPE_HASH:
            # Must be valid hex string of length 64 (SHA-256)
            if len(value) != 64:
                return False
            try:
                int(value, 16)
                return True
            except ValueError:
                return False
        elif signal_type == SignalType.SESSION_ID:
            return len(value) <= 64
        elif signal_type == SignalType.EVENT_TYPE:
            return value in ["task_completed", "priority_changed", "task_grouped"]
        elif signal_type == SignalType.PRIORITY_CHANGE:
            # Format: "low->high", "medium->high", etc.
            parts = value.split("->")
            if len(parts) != 2:
                return False
            valid_priorities = ["low", "medium", "high"]
            return parts[0] in valid_priorities and parts[1] in valid_priorities

        return True

    @classmethod
    def hash_task_type(cls, task_type: str) -> str:
        """
        Create one-way hash of task type for pattern identification.

        IMPORTANT: This hash is NOT reversible to original content.
        Only use generic task type identifiers, NOT task titles or descriptions.

        Args:
            task_type: Generic task type identifier (e.g., "email", "meeting", "coding")

        Returns:
            SHA-256 hex digest of task type
        """
        return hashlib.sha256(task_type.encode('utf-8')).hexdigest()

    @classmethod
    def validate_behavioral_event(cls, event_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Comprehensive validation of behavioral event data.

        Ensures:
        1. Only learnable signals are present
        2. No forbidden signals are included
        3. All signal values meet validation rules

        Args:
            event_data: Dictionary of event data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for forbidden signals
        for key in event_data.keys():
            if cls.is_signal_forbidden(key):
                return False, f"Forbidden signal detected: {key}"

        # Validate each learnable signal
        for key, value in event_data.items():
            if not cls.is_signal_learnable(key):
                return False, f"Unknown or unlearnable signal: {key}"

            try:
                signal_type = SignalType(key)
                if not cls.validate_signal_data(signal_type, value):
                    return False, f"Invalid data for signal {key}: {value}"
            except ValueError:
                return False, f"Invalid signal type: {key}"

        return True, ""

    @classmethod
    def get_privacy_summary(cls) -> Dict[str, List[str]]:
        """
        Generate human-readable summary of privacy policy.

        Returns:
            Dictionary with "learnable" and "forbidden" signal lists
        """
        return {
            "learnable": [
                f"{sig.value}: {spec.description}"
                for sig, spec in cls.LEARNABLE_SIGNALS.items()
            ],
            "forbidden": [
                f"{sig.value}: NEVER learned or stored"
                for sig in cls.FORBIDDEN_SIGNALS
            ]
        }
