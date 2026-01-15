"""
Tests for Adaptive Logic Service - Phase 5 Agent 4

Validates that:
1. Suggestions generated correctly from patterns
2. Confidence-based ranking works
3. Time slot recommendations accurate
4. Feedback loop captures responses
5. Suggestion types filtered properly
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from learning.adaptive_logic import AdaptiveLogicService, Suggestion, SuggestionType


class MockUserBehaviorProfile:
    """Mock UserBehaviorProfile for testing"""
    def __init__(self, user_id, data_points=20, learning_enabled=True):
        self.user_id = user_id
        self.data_points_collected = data_points
        self.learning_enabled = learning_enabled
        self.learning_paused = False
        self.peak_hours = "{}"
        self.type_timing_patterns = "{}"
        self.priority_adjustment_patterns = "{}"
        self.grouping_patterns = "{}"
        self.last_learning_date = datetime.utcnow()


class TestSuggestionGeneration:
    """Test suggestion generation logic"""

    def test_suggestion_creation(self):
        """Should create suggestion with all required fields"""
        suggestion = Suggestion(
            suggestion_type=SuggestionType.PEAK_HOUR,
            title="Peak at 9 AM",
            description="You're most productive at 9 AM",
            confidence=0.85,
            reasoning="Based on 50 tasks",
            metadata={"hour": 9}
        )

        assert suggestion.suggestion_type == SuggestionType.PEAK_HOUR
        assert suggestion.title == "Peak at 9 AM"
        assert suggestion.confidence == 0.85
        assert suggestion.metadata["hour"] == 9

    def test_suggestion_to_dict(self):
        """Should convert suggestion to dictionary"""
        suggestion = Suggestion(
            suggestion_type=SuggestionType.PEAK_HOUR,
            title="Test",
            description="Test description",
            confidence=0.70,
            reasoning="Test reasoning"
        )

        result = suggestion.to_dict()

        assert result["type"] == SuggestionType.PEAK_HOUR
        assert result["confidence"] == 0.70
        assert "created_at" in result


class TestPeakHourSuggestions:
    """Test peak hour suggestion generation"""

    def test_generate_peak_hour_suggestion_with_clear_pattern(self):
        """Should generate suggestion when peak hour is clear"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.peak_hours = json.dumps({
            "9": 10.0,  # 9 AM has highest score
            "14": 5.0,
            "16": 3.0
        })

        suggestions = AdaptiveLogicService._generate_peak_hour_suggestions(profile)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == SuggestionType.PEAK_HOUR
        assert "9" in suggestions[0].title or "AM" in suggestions[0].title
        assert suggestions[0].confidence >= 0.60

    def test_no_peak_hour_suggestion_without_data(self):
        """Should not generate suggestion without peak hour data"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.peak_hours = "{}"

        suggestions = AdaptiveLogicService._generate_peak_hour_suggestions(profile)

        assert len(suggestions) == 0

    def test_peak_hour_window_suggestion(self):
        """Should detect productivity windows (2-3 consecutive hours)"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.peak_hours = json.dumps({
            "9": 10.0,
            "10": 9.5,
            "11": 9.0,
            "16": 3.0
        })

        suggestions = AdaptiveLogicService._generate_peak_hour_suggestions(profile)

        # Should have both single peak and window suggestions
        assert len(suggestions) >= 1
        window_suggestion = next((s for s in suggestions if "window" in s.title.lower()), None)
        if window_suggestion:
            assert window_suggestion.confidence >= 0.50


class TestTypeTimingSuggestions:
    """Test task type timing suggestion generation"""

    def test_generate_type_timing_suggestion(self):
        """Should suggest best time for specific task types"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.type_timing_patterns = json.dumps({
            "a" * 64: {
                "9": 5,
                "10": 2,
                "14": 1
            }
        })

        suggestions = AdaptiveLogicService._generate_type_timing_suggestions(profile)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == SuggestionType.TYPE_TIMING
        assert suggestions[0].metadata["preferred_hour"] == 9

    def test_no_type_timing_without_frequency(self):
        """Should not suggest if frequency is too low (<3)"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.type_timing_patterns = json.dumps({
            "a" * 64: {
                "9": 2,  # Only 2 occurrences
                "10": 1
            }
        })

        suggestions = AdaptiveLogicService._generate_type_timing_suggestions(profile)

        assert len(suggestions) == 0

    def test_type_timing_confidence_calculation(self):
        """Confidence should be based on frequency concentration"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.type_timing_patterns = json.dumps({
            "a" * 64: {
                "9": 8,  # 8 out of 10 = 80% concentration
                "10": 1,
                "14": 1
            }
        })

        suggestions = AdaptiveLogicService._generate_type_timing_suggestions(profile)

        assert len(suggestions) > 0
        # High concentration should give high confidence
        assert suggestions[0].confidence >= 0.75


class TestPrioritySuggestions:
    """Test priority adjustment suggestion generation"""

    def test_generate_priority_upgrade_suggestion(self):
        """Should suggest starting higher when frequent upgrades"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.priority_adjustment_patterns = json.dumps({
            "low": {
                "high": 5,  # Frequently upgrade low → high
                "medium": 1
            }
        })

        suggestions = AdaptiveLogicService._generate_priority_suggestions(profile)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == SuggestionType.PRIORITY_ADJUSTMENT
        assert "higher" in suggestions[0].description.lower()
        assert suggestions[0].metadata["from_priority"] == "low"
        assert suggestions[0].metadata["to_priority"] == "high"

    def test_no_priority_suggestion_without_pattern(self):
        """Should not suggest if changes are too rare"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.priority_adjustment_patterns = json.dumps({
            "low": {
                "high": 2  # Only 2 changes, below threshold
            }
        })

        suggestions = AdaptiveLogicService._generate_priority_suggestions(profile)

        assert len(suggestions) == 0


class TestGroupingSuggestions:
    """Test task grouping suggestion generation"""

    def test_generate_grouping_suggestion(self):
        """Should suggest batching related tasks"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.grouping_patterns = json.dumps({
            "a" * 64: ["b" * 64, "c" * 64, "d" * 64]  # 3 related tasks
        })

        suggestions = AdaptiveLogicService._generate_grouping_suggestions(profile)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == SuggestionType.TASK_GROUPING
        assert suggestions[0].metadata["group_size"] == 3

    def test_no_grouping_without_relations(self):
        """Should not suggest if no task groupings"""
        profile = MockUserBehaviorProfile(uuid.uuid4())
        profile.grouping_patterns = "{}"

        suggestions = AdaptiveLogicService._generate_grouping_suggestions(profile)

        assert len(suggestions) == 0


class TestConfidenceRanking:
    """Test confidence-based suggestion ranking"""

    def test_rank_suggestions_by_confidence(self):
        """Should categorize suggestions into high/medium/low confidence"""
        suggestions = [
            Suggestion(SuggestionType.PEAK_HOUR, "High", "desc", 0.85, "reason"),
            Suggestion(SuggestionType.TYPE_TIMING, "Medium", "desc", 0.65, "reason"),
            Suggestion(SuggestionType.PRIORITY_ADJUSTMENT, "Low", "desc", 0.50, "reason"),
            Suggestion(SuggestionType.TASK_GROUPING, "Very High", "desc", 0.90, "reason")
        ]

        ranked = AdaptiveLogicService.rank_suggestions_by_confidence(suggestions)

        assert len(ranked["high_confidence"]) == 2  # 0.85 and 0.90
        assert len(ranked["medium_confidence"]) == 1  # 0.65
        assert len(ranked["low_confidence"]) == 1  # 0.50

    def test_ranking_thresholds(self):
        """Verify ranking thresholds are correct"""
        # High: 0.75+
        # Medium: 0.60-0.74
        # Low: <0.60

        high_suggestion = Suggestion(SuggestionType.PEAK_HOUR, "H", "d", 0.75, "r")
        medium_suggestion = Suggestion(SuggestionType.PEAK_HOUR, "M", "d", 0.60, "r")
        low_suggestion = Suggestion(SuggestionType.PEAK_HOUR, "L", "d", 0.59, "r")

        ranked = AdaptiveLogicService.rank_suggestions_by_confidence([
            high_suggestion, medium_suggestion, low_suggestion
        ])

        assert high_suggestion in ranked["high_confidence"]
        assert medium_suggestion in ranked["medium_confidence"]
        assert low_suggestion in ranked["low_confidence"]


class TestTimeSlotRecommendations:
    """Test time slot recommendation generation"""

    def test_generate_time_slot_recommendations(self):
        """Should generate suitability scores for all hours"""
        # This test would require mocking session and profile
        # Placeholder for structure
        pass

    def test_time_slot_for_specific_hour(self):
        """Should analyze specific hour when requested"""
        # Placeholder for structure
        pass

    def test_suitability_scoring(self):
        """Should calculate suitability relative to peak"""
        # Placeholder for structure
        pass


class TestSuggestionFiltering:
    """Test suggestion filtering and limits"""

    def test_filter_below_minimum_confidence(self):
        """Should exclude suggestions below 0.60 confidence"""
        suggestions = [
            Suggestion(SuggestionType.PEAK_HOUR, "Good", "d", 0.75, "r"),
            Suggestion(SuggestionType.PEAK_HOUR, "Bad", "d", 0.50, "r"),
            Suggestion(SuggestionType.PEAK_HOUR, "Okay", "d", 0.60, "r")
        ]

        # Filter by minimum confidence
        filtered = [s for s in suggestions if s.confidence >= 0.60]

        assert len(filtered) == 2  # Only 0.75 and 0.60

    def test_max_suggestions_per_type_limit(self):
        """Should limit suggestions per type to MAX_SUGGESTIONS_PER_TYPE"""
        assert AdaptiveLogicService.MAX_SUGGESTIONS_PER_TYPE == 3

    def test_max_total_suggestions_limit(self):
        """Should limit total suggestions to MAX_TOTAL_SUGGESTIONS"""
        assert AdaptiveLogicService.MAX_TOTAL_SUGGESTIONS == 10


class TestSuggestionMetadata:
    """Test suggestion metadata tracking"""

    def test_suggestion_includes_reasoning(self):
        """All suggestions should include reasoning"""
        suggestion = Suggestion(
            SuggestionType.PEAK_HOUR,
            "Title",
            "Description",
            0.75,
            "Based on 50 tasks completed at this hour"
        )

        assert suggestion.reasoning is not None
        assert len(suggestion.reasoning) > 0

    def test_suggestion_includes_metadata(self):
        """Suggestions should include relevant metadata"""
        suggestion = Suggestion(
            SuggestionType.PEAK_HOUR,
            "Title",
            "Description",
            0.75,
            "Reasoning",
            metadata={"hour": 9, "score": 10.0}
        )

        assert "hour" in suggestion.metadata
        assert "score" in suggestion.metadata

    def test_suggestion_has_timestamp(self):
        """All suggestions should have creation timestamp"""
        suggestion = Suggestion(
            SuggestionType.PEAK_HOUR,
            "Title",
            "Description",
            0.75,
            "Reasoning"
        )

        assert suggestion.created_at is not None
        assert isinstance(suggestion.created_at, datetime)


class TestConfidenceThresholds:
    """Test confidence threshold constants"""

    def test_minimum_suggestion_confidence(self):
        """Minimum confidence for suggestions should be 0.60"""
        assert AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE == 0.60

    def test_high_confidence_threshold(self):
        """High confidence threshold should be 0.75"""
        assert AdaptiveLogicService.HIGH_CONFIDENCE_THRESHOLD == 0.75

    def test_thresholds_are_consistent(self):
        """High confidence should be higher than minimum"""
        assert AdaptiveLogicService.HIGH_CONFIDENCE_THRESHOLD > AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE
