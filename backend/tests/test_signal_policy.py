"""
Tests for Signal Policy - Phase 5 Agent 1

Validates that learning signal policy correctly identifies:
1. Learnable signals (privacy-safe metadata)
2. Forbidden signals (privacy violations)
3. Signal data validation rules

Critical: These tests ensure NO privacy violations occur.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from learning.signal_policy import (
    SignalPolicy,
    SignalType,
    ForbiddenSignalType,
    LearnableSignal
)


class TestLearnableSignals:
    """Test that only approved signals are learnable"""

    def test_hour_of_day_is_learnable(self):
        """Hour of day (0-23) should be learnable"""
        assert SignalPolicy.is_signal_learnable("hour_of_day")

    def test_day_of_week_is_learnable(self):
        """Day of week (0-6) should be learnable"""
        assert SignalPolicy.is_signal_learnable("day_of_week")

    def test_task_type_hash_is_learnable(self):
        """Task type hash (SHA-256) should be learnable"""
        assert SignalPolicy.is_signal_learnable("task_type_hash")

    def test_session_id_is_learnable(self):
        """Session ID for grouping should be learnable"""
        assert SignalPolicy.is_signal_learnable("session_id")

    def test_event_type_is_learnable(self):
        """Event type should be learnable"""
        assert SignalPolicy.is_signal_learnable("event_type")

    def test_priority_change_is_learnable(self):
        """Priority change patterns should be learnable"""
        assert SignalPolicy.is_signal_learnable("priority_change")

    def test_unknown_signal_not_learnable(self):
        """Unknown signals should NOT be learnable"""
        assert not SignalPolicy.is_signal_learnable("unknown_signal")


class TestForbiddenSignals:
    """Test that privacy-violating signals are forbidden"""

    def test_task_title_forbidden(self):
        """Task title must be forbidden (privacy violation)"""
        assert SignalPolicy.is_signal_forbidden("task_title")

    def test_task_description_forbidden(self):
        """Task description must be forbidden (privacy violation)"""
        assert SignalPolicy.is_signal_forbidden("task_description")

    def test_task_notes_forbidden(self):
        """Task notes must be forbidden (privacy violation)"""
        assert SignalPolicy.is_signal_forbidden("task_notes")

    def test_user_category_forbidden(self):
        """User-defined categories must be forbidden (privacy violation)"""
        assert SignalPolicy.is_signal_forbidden("user_category")

    def test_user_tag_forbidden(self):
        """User-defined tags must be forbidden (privacy violation)"""
        assert SignalPolicy.is_signal_forbidden("user_tag")

    def test_user_email_forbidden(self):
        """User email must be forbidden (PII)"""
        assert SignalPolicy.is_signal_forbidden("user_email")

    def test_user_name_forbidden(self):
        """User name must be forbidden (PII)"""
        assert SignalPolicy.is_signal_forbidden("user_name")


class TestSignalValidation:
    """Test signal data validation rules"""

    def test_valid_hour_of_day(self):
        """Valid hour (0-23) should pass validation"""
        assert SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, 14)
        assert SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, 0)
        assert SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, 23)

    def test_invalid_hour_of_day(self):
        """Invalid hour should fail validation"""
        assert not SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, -1)
        assert not SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, 24)
        assert not SignalPolicy.validate_signal_data(SignalType.HOUR_OF_DAY, 100)

    def test_valid_day_of_week(self):
        """Valid day (0-6) should pass validation"""
        assert SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, 0)
        assert SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, 3)
        assert SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, 6)

    def test_invalid_day_of_week(self):
        """Invalid day should fail validation"""
        assert not SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, -1)
        assert not SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, 7)
        assert not SignalPolicy.validate_signal_data(SignalType.DAY_OF_WEEK, 10)

    def test_valid_task_type_hash(self):
        """Valid SHA-256 hash (64 hex chars) should pass"""
        valid_hash = "a" * 64
        assert SignalPolicy.validate_signal_data(SignalType.TASK_TYPE_HASH, valid_hash)

    def test_invalid_task_type_hash_length(self):
        """Invalid hash length should fail"""
        assert not SignalPolicy.validate_signal_data(SignalType.TASK_TYPE_HASH, "abc")
        assert not SignalPolicy.validate_signal_data(SignalType.TASK_TYPE_HASH, "a" * 32)

    def test_invalid_task_type_hash_format(self):
        """Non-hexadecimal hash should fail"""
        invalid_hash = "z" * 64  # 'z' is not hex
        assert not SignalPolicy.validate_signal_data(SignalType.TASK_TYPE_HASH, invalid_hash)

    def test_valid_session_id(self):
        """Valid session ID (≤64 chars) should pass"""
        assert SignalPolicy.validate_signal_data(SignalType.SESSION_ID, "sess_abc123")
        assert SignalPolicy.validate_signal_data(SignalType.SESSION_ID, "x" * 64)

    def test_invalid_session_id_too_long(self):
        """Session ID >64 chars should fail"""
        assert not SignalPolicy.validate_signal_data(SignalType.SESSION_ID, "x" * 65)

    def test_valid_event_type(self):
        """Valid event types should pass"""
        assert SignalPolicy.validate_signal_data(SignalType.EVENT_TYPE, "task_completed")
        assert SignalPolicy.validate_signal_data(SignalType.EVENT_TYPE, "priority_changed")
        assert SignalPolicy.validate_signal_data(SignalType.EVENT_TYPE, "task_grouped")

    def test_invalid_event_type(self):
        """Invalid event types should fail"""
        assert not SignalPolicy.validate_signal_data(SignalType.EVENT_TYPE, "unknown_event")
        assert not SignalPolicy.validate_signal_data(SignalType.EVENT_TYPE, "task_deleted")

    def test_valid_priority_change(self):
        """Valid priority change patterns should pass"""
        assert SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "low->high")
        assert SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "medium->high")
        assert SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "high->low")

    def test_invalid_priority_change_format(self):
        """Invalid priority change format should fail"""
        assert not SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "low-high")
        assert not SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "low")
        assert not SignalPolicy.validate_signal_data(SignalType.PRIORITY_CHANGE, "low->invalid")


class TestTaskTypeHashing:
    """Test one-way hashing of task types"""

    def test_hash_task_type_returns_sha256(self):
        """Hash should return 64-character hex string"""
        hash_result = SignalPolicy.hash_task_type("email")
        assert len(hash_result) == 64
        # Verify it's hexadecimal
        int(hash_result, 16)

    def test_hash_task_type_consistent(self):
        """Same input should produce same hash"""
        hash1 = SignalPolicy.hash_task_type("meeting")
        hash2 = SignalPolicy.hash_task_type("meeting")
        assert hash1 == hash2

    def test_hash_task_type_unique(self):
        """Different inputs should produce different hashes"""
        hash1 = SignalPolicy.hash_task_type("email")
        hash2 = SignalPolicy.hash_task_type("meeting")
        assert hash1 != hash2


class TestBehavioralEventValidation:
    """Test comprehensive behavioral event validation"""

    def test_valid_behavioral_event(self):
        """Valid event with only learnable signals should pass"""
        event_data = {
            "event_type": "task_completed",
            "hour_of_day": 14,
            "day_of_week": 2,
            "task_type_hash": "a" * 64,
            "session_id": "sess_123"
        }
        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        assert is_valid
        assert error == ""

    def test_event_with_forbidden_signal_fails(self):
        """Event containing forbidden signal should fail"""
        event_data = {
            "event_type": "task_completed",
            "hour_of_day": 14,
            "task_title": "Buy groceries"  # FORBIDDEN
        }
        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        assert not is_valid
        assert "Forbidden signal" in error
        assert "task_title" in error

    def test_event_with_task_description_fails(self):
        """Event containing task description should fail (privacy violation)"""
        event_data = {
            "event_type": "task_completed",
            "task_description": "Go to store"  # FORBIDDEN
        }
        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        assert not is_valid
        assert "task_description" in error

    def test_event_with_invalid_signal_data_fails(self):
        """Event with invalid signal data should fail"""
        event_data = {
            "hour_of_day": 25,  # Invalid: must be 0-23
            "day_of_week": 2
        }
        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        assert not is_valid
        assert "Invalid data" in error

    def test_event_with_unknown_signal_fails(self):
        """Event with unknown signal should fail"""
        event_data = {
            "hour_of_day": 14,
            "unknown_field": "value"
        }
        is_valid, error = SignalPolicy.validate_behavioral_event(event_data)
        assert not is_valid
        assert "unlearnable signal" in error or "Unknown" in error


class TestPrivacySummary:
    """Test privacy policy summary generation"""

    def test_privacy_summary_contains_learnable_signals(self):
        """Privacy summary should list all learnable signals"""
        summary = SignalPolicy.get_privacy_summary()
        assert "learnable" in summary
        assert len(summary["learnable"]) == 6  # 6 learnable signals

    def test_privacy_summary_contains_forbidden_signals(self):
        """Privacy summary should list all forbidden signals"""
        summary = SignalPolicy.get_privacy_summary()
        assert "forbidden" in summary
        assert len(summary["forbidden"]) == 9  # 9 forbidden signals

    def test_privacy_summary_learnable_includes_descriptions(self):
        """Learnable signals should include descriptions"""
        summary = SignalPolicy.get_privacy_summary()
        for item in summary["learnable"]:
            assert ":" in item  # Format: "signal_name: description"

    def test_privacy_summary_forbidden_marked_never(self):
        """Forbidden signals should be marked as NEVER learned"""
        summary = SignalPolicy.get_privacy_summary()
        for item in summary["forbidden"]:
            assert "NEVER" in item
