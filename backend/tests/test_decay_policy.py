"""
Tests for Decay and Forgetting Policy - Phase 5 Agent 1 (Tasks 1.3 & 1.4)

Validates that:
1. Signal decay weights are calculated correctly
2. Forgetting rules trigger appropriately
3. Recent data is weighted more than old data
4. Stale patterns are automatically removed
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from learning.decay_policy import (
    DecayPolicy,
    ForgettingPolicy,
    ForgettingTrigger,
    DecayProfile
)


class TestDecayWeightCalculation:
    """Test time-based decay weight calculations"""

    def test_fresh_signal_full_weight(self):
        """Signals 0 days old should have full weight (1.0)"""
        weight = DecayPolicy.calculate_decay_weight(0, "peak_hours")
        assert weight == 1.0

    def test_half_life_signal_half_weight(self):
        """Signals at half-life should have ~0.5 weight"""
        # peak_hours has 30-day half-life
        weight = DecayPolicy.calculate_decay_weight(30, "peak_hours")
        assert 0.45 <= weight <= 0.55

    def test_old_signal_low_weight(self):
        """Very old signals should have low weight"""
        # 90 days old should be significantly decayed
        weight = DecayPolicy.calculate_decay_weight(90, "peak_hours")
        assert weight < 0.2

    def test_priority_decays_faster_than_grouping(self):
        """Priority patterns should decay faster than grouping patterns"""
        days = 30
        priority_weight = DecayPolicy.calculate_decay_weight(days, "priority_adjustment")
        grouping_weight = DecayPolicy.calculate_decay_weight(days, "grouping")
        assert priority_weight < grouping_weight

    def test_decay_weight_never_negative(self):
        """Decay weight should never be negative"""
        weight = DecayPolicy.calculate_decay_weight(1000, "peak_hours")
        assert weight >= 0.0

    def test_decay_weight_never_exceeds_one(self):
        """Decay weight should never exceed 1.0"""
        weight = DecayPolicy.calculate_decay_weight(0, "peak_hours")
        assert weight <= 1.0


class TestAgeBucketWeights:
    """Test simplified bucket-based decay weights"""

    def test_recent_bucket_full_weight(self):
        """0-30 days: full weight (1.0)"""
        assert DecayPolicy.get_age_bucket_weight(0) == 1.0
        assert DecayPolicy.get_age_bucket_weight(15) == 1.0
        assert DecayPolicy.get_age_bucket_weight(30) == 1.0

    def test_medium_age_bucket(self):
        """31-60 days: 70% weight"""
        assert DecayPolicy.get_age_bucket_weight(31) == 0.7
        assert DecayPolicy.get_age_bucket_weight(45) == 0.7
        assert DecayPolicy.get_age_bucket_weight(60) == 0.7

    def test_older_bucket(self):
        """61-90 days: 40% weight"""
        assert DecayPolicy.get_age_bucket_weight(61) == 0.4
        assert DecayPolicy.get_age_bucket_weight(75) == 0.4
        assert DecayPolicy.get_age_bucket_weight(90) == 0.4

    def test_very_old_bucket(self):
        """91+ days: 20% weight"""
        assert DecayPolicy.get_age_bucket_weight(91) == 0.2
        assert DecayPolicy.get_age_bucket_weight(180) == 0.2
        assert DecayPolicy.get_age_bucket_weight(365) == 0.2


class TestForgettingRules:
    """Test pattern forgetting triggers"""

    def test_fresh_pattern_not_forgotten(self):
        """Recent, high-confidence patterns should NOT be forgotten"""
        last_updated = datetime.utcnow() - timedelta(days=10)
        should_forget, trigger = DecayPolicy.should_forget_pattern(
            pattern_type="peak_hours",
            last_updated=last_updated,
            confidence_score=0.75,
            data_points_count=50
        )
        assert not should_forget
        assert trigger is None

    def test_age_threshold_triggers_forgetting(self):
        """Patterns older than max_age_days should be forgotten"""
        # peak_hours max_age is 90 days
        last_updated = datetime.utcnow() - timedelta(days=100)
        should_forget, trigger = DecayPolicy.should_forget_pattern(
            pattern_type="peak_hours",
            last_updated=last_updated,
            confidence_score=0.75,
            data_points_count=50
        )
        assert should_forget
        assert trigger == ForgettingTrigger.AGE_THRESHOLD

    def test_inactivity_triggers_forgetting(self):
        """No updates in 60+ days should trigger forgetting"""
        last_updated = datetime.utcnow() - timedelta(days=65)
        should_forget, trigger = DecayPolicy.should_forget_pattern(
            pattern_type="peak_hours",
            last_updated=last_updated,
            confidence_score=0.75,
            data_points_count=50
        )
        assert should_forget
        assert trigger == ForgettingTrigger.INACTIVITY

    def test_low_confidence_triggers_forgetting(self):
        """Confidence below min_confidence should trigger forgetting"""
        last_updated = datetime.utcnow() - timedelta(days=10)
        should_forget, trigger = DecayPolicy.should_forget_pattern(
            pattern_type="peak_hours",
            last_updated=last_updated,
            confidence_score=0.30,  # Below 0.50 threshold
            data_points_count=50
        )
        assert should_forget
        assert trigger == ForgettingTrigger.LOW_CONFIDENCE

    def test_insufficient_data_triggers_forgetting(self):
        """Less than 3 data points should trigger forgetting"""
        last_updated = datetime.utcnow() - timedelta(days=10)
        should_forget, trigger = DecayPolicy.should_forget_pattern(
            pattern_type="peak_hours",
            last_updated=last_updated,
            confidence_score=0.75,
            data_points_count=2  # Less than 3
        )
        assert should_forget
        assert trigger == ForgettingTrigger.LOW_CONFIDENCE


class TestRecencyWeight:
    """Test recency weight calculations for confidence scoring"""

    def test_recent_event_high_weight(self):
        """Events from today should have high recency weight"""
        recent_time = datetime.utcnow()
        weight = DecayPolicy.calculate_recency_weight(recent_time)
        assert weight >= 0.95

    def test_month_old_event_medium_weight(self):
        """Events from 30 days ago should have ~0.5 weight"""
        month_ago = datetime.utcnow() - timedelta(days=30)
        weight = DecayPolicy.calculate_recency_weight(month_ago)
        assert 0.4 <= weight <= 0.6

    def test_old_event_low_weight(self):
        """Events from 90 days ago should have low weight"""
        old_time = datetime.utcnow() - timedelta(days=90)
        weight = DecayPolicy.calculate_recency_weight(old_time)
        assert weight < 0.2


class TestEventFiltering:
    """Test filtering of events by age"""

    def test_filter_keeps_recent_events(self):
        """Recent events should be kept"""
        events = [
            {"id": 1, "timestamp": datetime.utcnow() - timedelta(days=10)},
            {"id": 2, "timestamp": datetime.utcnow() - timedelta(days=30)},
        ]
        filtered = DecayPolicy.filter_recent_events(events, max_age_days=90)
        assert len(filtered) == 2

    def test_filter_removes_old_events(self):
        """Events older than max_age_days should be removed"""
        events = [
            {"id": 1, "timestamp": datetime.utcnow() - timedelta(days=10)},
            {"id": 2, "timestamp": datetime.utcnow() - timedelta(days=100)},
        ]
        filtered = DecayPolicy.filter_recent_events(events, max_age_days=90)
        assert len(filtered) == 1
        assert filtered[0]["id"] == 1

    def test_filter_all_old_events(self):
        """All old events should be filtered out"""
        events = [
            {"id": 1, "timestamp": datetime.utcnow() - timedelta(days=100)},
            {"id": 2, "timestamp": datetime.utcnow() - timedelta(days=200)},
        ]
        filtered = DecayPolicy.filter_recent_events(events, max_age_days=90)
        assert len(filtered) == 0


class TestPatternScoreDecay:
    """Test decay application to pattern scores"""

    def test_fresh_patterns_no_decay(self):
        """Fresh patterns should have minimal decay"""
        pattern_scores = {"9": 0.8, "14": 0.9, "22": 0.7}
        last_updated = datetime.utcnow()
        decayed = DecayPolicy.apply_decay_to_pattern_scores(
            pattern_scores, last_updated, "peak_hours"
        )
        # Should be very close to original
        assert decayed["14"] >= 0.85

    def test_old_patterns_significant_decay(self):
        """Old patterns should decay significantly"""
        pattern_scores = {"9": 0.8, "14": 0.9, "22": 0.7}
        last_updated = datetime.utcnow() - timedelta(days=90)
        decayed = DecayPolicy.apply_decay_to_pattern_scores(
            pattern_scores, last_updated, "peak_hours"
        )
        # Should be significantly reduced
        assert decayed["14"] < 0.3

    def test_decay_maintains_relative_order(self):
        """Decay should maintain relative ranking of scores"""
        pattern_scores = {"low": 0.5, "high": 0.9}
        last_updated = datetime.utcnow() - timedelta(days=30)
        decayed = DecayPolicy.apply_decay_to_pattern_scores(
            pattern_scores, last_updated, "peak_hours"
        )
        # High should still be higher than low
        assert decayed["high"] > decayed["low"]


class TestPatternRetention:
    """Test pattern retention decisions"""

    def test_retain_healthy_pattern(self):
        """Healthy patterns should be retained"""
        should_retain = ForgettingPolicy.should_retain_pattern(
            pattern_type="peak_hours",
            confidence=0.75,
            data_points=50,
            last_updated=datetime.utcnow() - timedelta(days=10)
        )
        assert should_retain

    def test_forget_unhealthy_pattern(self):
        """Unhealthy patterns should NOT be retained"""
        should_retain = ForgettingPolicy.should_retain_pattern(
            pattern_type="peak_hours",
            confidence=0.25,  # Low confidence
            data_points=2,    # Insufficient data
            last_updated=datetime.utcnow() - timedelta(days=100)  # Too old
        )
        assert not should_retain


class TestPatternPruning:
    """Test automatic pruning of old patterns"""

    def test_prune_keeps_healthy_patterns(self):
        """Healthy patterns should survive pruning"""
        patterns = {
            "peak_hours": {
                "confidence": 0.75,
                "data_points": 50,
                "last_updated": datetime.utcnow() - timedelta(days=10)
            },
            "type_timing": {
                "confidence": 0.80,
                "data_points": 30,
                "last_updated": datetime.utcnow() - timedelta(days=20)
            }
        }
        pruned = ForgettingPolicy.prune_old_patterns(patterns)
        assert len(pruned) == 2
        assert "peak_hours" in pruned
        assert "type_timing" in pruned

    def test_prune_removes_unhealthy_patterns(self):
        """Unhealthy patterns should be pruned"""
        patterns = {
            "peak_hours": {
                "confidence": 0.75,
                "data_points": 50,
                "last_updated": datetime.utcnow() - timedelta(days=10)
            },
            "type_timing": {
                "confidence": 0.30,  # Low confidence
                "data_points": 2,    # Insufficient data
                "last_updated": datetime.utcnow() - timedelta(days=100)  # Too old
            }
        }
        pruned = ForgettingPolicy.prune_old_patterns(patterns)
        assert len(pruned) == 1
        assert "peak_hours" in pruned
        assert "type_timing" not in pruned


class TestForgettingExplanations:
    """Test human-readable forgetting explanations"""

    def test_age_threshold_explanation(self):
        """Age threshold trigger should have clear explanation"""
        explanation = ForgettingPolicy.get_forgetting_explanation(
            ForgettingTrigger.AGE_THRESHOLD
        )
        assert "old" in explanation.lower()
        assert "relevant" in explanation.lower()

    def test_inactivity_explanation(self):
        """Inactivity trigger should have clear explanation"""
        explanation = ForgettingPolicy.get_forgetting_explanation(
            ForgettingTrigger.INACTIVITY
        )
        assert "activity" in explanation.lower()

    def test_low_confidence_explanation(self):
        """Low confidence trigger should have clear explanation"""
        explanation = ForgettingPolicy.get_forgetting_explanation(
            ForgettingTrigger.LOW_CONFIDENCE
        )
        assert "confidence" in explanation.lower()

    def test_user_reset_explanation(self):
        """User reset trigger should have clear explanation"""
        explanation = ForgettingPolicy.get_forgetting_explanation(
            ForgettingTrigger.USER_RESET
        )
        assert "reset" in explanation.lower()
        assert "you" in explanation.lower() or "You" in explanation
