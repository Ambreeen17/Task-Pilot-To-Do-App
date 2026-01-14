"""
Tests for Pattern Detection Service - Phase 5 Agent 3 (Tasks 3.3-3.7)

Validates that:
1. Peak hours patterns detected correctly
2. Type timing patterns identified
3. Priority adjustment patterns recognized
4. Task grouping patterns found
5. Confidence scores calculated properly
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from learning.pattern_detection import PatternDetectionService
from models.behavioral_event import BehavioralEvent


class MockEvent:
    """Mock BehavioralEvent for testing"""
    def __init__(self, event_type, hour, day, type_hash, timestamp, session_id=None,
                 from_priority=None, to_priority=None):
        self.user_id = uuid.uuid4()
        self.event_type = event_type
        self.hour_of_day = hour
        self.day_of_week = day
        self.task_type_hash = type_hash
        self.timestamp = timestamp
        self.session_id = session_id
        self.from_priority = from_priority
        self.to_priority = to_priority


class TestPeakHoursDetection:
    """Test peak productivity hours detection"""

    def test_detect_peak_hours_with_clear_pattern(self):
        """Should detect peak hours when pattern is clear"""
        # Create events clustered around 9am and 2pm
        events = []
        now = datetime.utcnow()

        for i in range(10):
            # 9am completions
            events.append(MockEvent(
                "task_completed", 9, 1, "a" * 64,
                now - timedelta(days=i)
            ))
            # 2pm completions
            events.append(MockEvent(
                "task_completed", 14, 1, "a" * 64,
                now - timedelta(days=i)
            ))

        hour_scores, confidence, data_points = PatternDetectionService.detect_peak_hours(events)

        assert 9 in hour_scores
        assert 14 in hour_scores
        assert confidence > 0.4  # Above minimum threshold
        assert data_points == 20

    def test_detect_peak_hours_insufficient_data(self):
        """Should return empty when insufficient data"""
        events = [
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow()),
            MockEvent("task_completed", 10, 1, "a" * 64, datetime.utcnow())
        ]

        hour_scores, confidence, data_points = PatternDetectionService.detect_peak_hours(events, min_occurrences=3)

        assert hour_scores == {}
        assert confidence == 0.0
        assert data_points == 0

    def test_detect_peak_hours_applies_decay(self):
        """Recent events should have higher weight than old events"""
        events = []
        now = datetime.utcnow()

        # 5 recent events at 9am
        for i in range(5):
            events.append(MockEvent(
                "task_completed", 9, 1, "a" * 64,
                now - timedelta(days=i)
            ))

        # 5 old events at 2pm (90 days ago)
        for i in range(5):
            events.append(MockEvent(
                "task_completed", 14, 1, "a" * 64,
                now - timedelta(days=90 + i)
            ))

        hour_scores, confidence, data_points = PatternDetectionService.detect_peak_hours(events)

        # Recent 9am should score higher than old 2pm due to decay
        assert hour_scores[9] > hour_scores.get(14, 0)


class TestTypeTimingPatterns:
    """Test task type timing pattern detection"""

    def test_detect_type_timing_patterns(self):
        """Should detect which hours are preferred for specific task types"""
        events = []
        now = datetime.utcnow()

        # Task type A at 9am
        for i in range(5):
            events.append(MockEvent(
                "task_completed", 9, 1, "a" * 64,
                now - timedelta(days=i)
            ))

        # Task type B at 2pm
        for i in range(5):
            events.append(MockEvent(
                "task_completed", 14, 1, "b" * 64,
                now - timedelta(days=i)
            ))

        patterns, confidence, data_points = PatternDetectionService.detect_type_timing_patterns(events)

        assert "a" * 64 in patterns
        assert "b" * 64 in patterns
        assert 9 in patterns["a" * 64]
        assert 14 in patterns["b" * 64]
        assert confidence > 0.4

    def test_type_timing_insufficient_data(self):
        """Should return empty with insufficient data per type"""
        events = [
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow()),
            MockEvent("task_completed", 10, 1, "a" * 64, datetime.utcnow())
        ]

        patterns, confidence, data_points = PatternDetectionService.detect_type_timing_patterns(events, min_occurrences=3)

        assert patterns == {}
        assert confidence == 0.0


class TestPriorityAdjustmentPatterns:
    """Test priority adjustment pattern detection"""

    def test_detect_priority_adjustment_patterns(self):
        """Should detect common priority changes"""
        events = []
        now = datetime.utcnow()

        # Low → High changes (5x)
        for i in range(5):
            events.append(MockEvent(
                "priority_changed", 9, 1, "a" * 64,
                now - timedelta(days=i),
                from_priority="low",
                to_priority="high"
            ))

        # Medium → High changes (3x)
        for i in range(3):
            events.append(MockEvent(
                "priority_changed", 14, 1, "a" * 64,
                now - timedelta(days=i),
                from_priority="medium",
                to_priority="high"
            ))

        patterns, confidence, data_points = PatternDetectionService.detect_priority_adjustment_patterns(events)

        assert "low" in patterns
        assert patterns["low"]["high"] >= 3
        assert "medium" in patterns
        assert patterns["medium"]["high"] >= 3
        assert confidence > 0.4
        assert data_points == 8

    def test_priority_adjustment_filters_non_priority_events(self):
        """Should only process priority_changed events"""
        events = [
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow()),
            MockEvent("priority_changed", 10, 1, "a" * 64, datetime.utcnow(),
                     from_priority="low", to_priority="high")
        ]

        patterns, confidence, data_points = PatternDetectionService.detect_priority_adjustment_patterns(events, min_occurrences=1)

        # Should only count the priority_changed event
        assert data_points == 1


class TestGroupingPatterns:
    """Test task grouping pattern detection"""

    def test_detect_grouping_patterns(self):
        """Should detect which task types are grouped together"""
        events = []
        now = datetime.utcnow()

        # Session 1: Types A and B grouped
        for task_type in ["a" * 64, "b" * 64]:
            events.append(MockEvent(
                "task_grouped", 9, 1, task_type,
                now, session_id="sess_1"
            ))

        # Session 2: Types A and B grouped again
        for task_type in ["a" * 64, "b" * 64]:
            events.append(MockEvent(
                "task_grouped", 10, 1, task_type,
                now, session_id="sess_2"
            ))

        # Session 3: Types A and B grouped again
        for task_type in ["a" * 64, "b" * 64]:
            events.append(MockEvent(
                "task_grouped", 11, 1, task_type,
                now, session_id="sess_3"
            ))

        patterns, confidence, data_points = PatternDetectionService.detect_grouping_patterns(events)

        assert "a" * 64 in patterns
        assert "b" * 64 in patterns["a" * 64]
        assert "a" * 64 in patterns["b" * 64]
        assert confidence > 0.4

    def test_grouping_patterns_requires_session_id(self):
        """Should only detect patterns when session_id is present"""
        events = [
            MockEvent("task_grouped", 9, 1, "a" * 64, datetime.utcnow(), session_id=None),
            MockEvent("task_grouped", 10, 1, "b" * 64, datetime.utcnow(), session_id=None)
        ]

        patterns, confidence, data_points = PatternDetectionService.detect_grouping_patterns(events)

        assert patterns == {}


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    def test_calculate_pattern_confidence(self):
        """Should calculate confidence using correct formula"""
        # Formula: (frequency * 0.4) + (recency * 0.3) + (consistency * 0.3)
        confidence = PatternDetectionService.calculate_pattern_confidence(
            data_points=20,  # Full frequency weight (20/20 = 1.0)
            recency_weight=1.0,  # Recent
            consistency_weight=1.0  # Consistent
        )

        assert confidence == 1.0

    def test_confidence_capped_at_one(self):
        """Confidence should never exceed 1.0"""
        confidence = PatternDetectionService.calculate_pattern_confidence(
            data_points=100,  # More than needed
            recency_weight=1.0,
            consistency_weight=1.0
        )

        assert confidence <= 1.0

    def test_confidence_low_with_insufficient_data(self):
        """Low data points should result in lower confidence"""
        confidence_low = PatternDetectionService.calculate_pattern_confidence(
            data_points=5,  # Low data points
            recency_weight=1.0,
            consistency_weight=1.0
        )

        confidence_high = PatternDetectionService.calculate_pattern_confidence(
            data_points=20,  # High data points
            recency_weight=1.0,
            consistency_weight=1.0
        )

        assert confidence_low < confidence_high


class TestSuggestionThresholds:
    """Test pattern suggestion thresholds"""

    def test_should_suggest_pattern_above_threshold(self):
        """Pattern above 0.60 confidence should be used for suggestions"""
        assert PatternDetectionService.should_suggest_pattern(0.75)
        assert PatternDetectionService.should_suggest_pattern(0.60)

    def test_should_not_suggest_pattern_below_threshold(self):
        """Pattern below 0.60 confidence should NOT be used for suggestions"""
        assert not PatternDetectionService.should_suggest_pattern(0.59)
        assert not PatternDetectionService.should_suggest_pattern(0.40)

    def test_custom_threshold(self):
        """Should respect custom threshold"""
        assert PatternDetectionService.should_suggest_pattern(0.50, threshold=0.45)
        assert not PatternDetectionService.should_suggest_pattern(0.50, threshold=0.55)


class TestMinimumOccurrences:
    """Test minimum occurrence requirements"""

    def test_peak_hours_requires_minimum_occurrences(self):
        """Should require at least 3 occurrences per pattern"""
        events = [
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow()),
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow())
        ]

        hour_scores, confidence, _ = PatternDetectionService.detect_peak_hours(events, min_occurrences=3)

        assert hour_scores == {}
        assert confidence == 0.0

    def test_minimum_occurrences_configurable(self):
        """Should allow custom minimum occurrence threshold"""
        events = [
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow()),
            MockEvent("task_completed", 9, 1, "a" * 64, datetime.utcnow())
        ]

        # With min_occurrences=2, should detect pattern
        hour_scores, confidence, _ = PatternDetectionService.detect_peak_hours(events, min_occurrences=2)

        assert 9 in hour_scores
        assert confidence > 0.0
