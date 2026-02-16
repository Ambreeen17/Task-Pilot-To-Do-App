"""
Adaptive Logic Service - Phase 5 Agent 4

Generates personalized suggestions based on detected behavioral patterns.
Uses confidence-based ranking to ensure high-quality recommendations.

Reference: ADR-002 Pattern Analysis and Confidence Scoring System
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlmodel import Session, select
import json
import logging

try:
    from ..models.behavioral_event import UserBehaviorProfile
    from ..models.preferences import UserPreferences
    from .pattern_detection import PatternDetectionService
except ImportError:
    from models.behavioral_event import UserBehaviorProfile
    from models.preferences import UserPreferences
    from learning.pattern_detection import PatternDetectionService

logger = logging.getLogger(__name__)


class SuggestionType:
    """Types of adaptive suggestions"""
    PEAK_HOUR = "peak_hour"
    TYPE_TIMING = "type_timing"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    TASK_GROUPING = "task_grouping"


class Suggestion:
    """Individual adaptive suggestion"""
    def __init__(
        self,
        suggestion_type: str,
        title: str,
        description: str,
        confidence: float,
        reasoning: str,
        actionable: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.suggestion_type = suggestion_type
        self.title = title
        self.description = description
        self.confidence = confidence
        self.reasoning = reasoning
        self.actionable = actionable
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "type": self.suggestion_type,
            "title": self.title,
            "description": self.description,
            "confidence": round(self.confidence, 2),
            "reasoning": self.reasoning,
            "actionable": self.actionable,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class AdaptiveLogicService:
    """
    Generates adaptive suggestions based on learned patterns.

    Confidence Thresholds:
    - 0.60+: Suggest to user
    - 0.75+: High confidence (show prominently)
    - <0.60: Don't suggest (pattern not strong enough)
    """

    # Confidence thresholds
    MIN_SUGGESTION_CONFIDENCE = 0.60
    HIGH_CONFIDENCE_THRESHOLD = 0.75

    # Suggestion limits
    MAX_SUGGESTIONS_PER_TYPE = 3
    MAX_TOTAL_SUGGESTIONS = 10

    @staticmethod
    def generate_all_suggestions(
        user_id: str,
        session: Session,
        filter_type: Optional[str] = None
    ) -> List[Suggestion]:
        """
        Generate all adaptive suggestions for user.

        Args:
            user_id: User UUID
            session: Database session
            filter_type: Optional filter for specific suggestion type

        Returns:
            List of Suggestion objects, ranked by confidence
        """
        # Get user profile
        import uuid
        profile = session.exec(
            select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == uuid.UUID(user_id))
        ).first()

        if not profile or profile.data_points_collected < 20:
            logger.debug(f"Insufficient data for suggestions (user {user_id})")
            return []

        # Check if learning is enabled
        prefs = session.exec(
            select(UserPreferences).where(UserPreferences.user_id == uuid.UUID(user_id))
        ).first()

        if not prefs or not prefs.learning_enabled or prefs.learning_paused:
            logger.debug(f"Learning disabled for user {user_id}")
            return []

        suggestions = []

        # Generate suggestions by type
        if not filter_type or filter_type == SuggestionType.PEAK_HOUR:
            suggestions.extend(
                AdaptiveLogicService._generate_peak_hour_suggestions(profile)
            )

        if not filter_type or filter_type == SuggestionType.TYPE_TIMING:
            suggestions.extend(
                AdaptiveLogicService._generate_type_timing_suggestions(profile)
            )

        if not filter_type or filter_type == SuggestionType.PRIORITY_ADJUSTMENT:
            suggestions.extend(
                AdaptiveLogicService._generate_priority_suggestions(profile)
            )

        if not filter_type or filter_type == SuggestionType.TASK_GROUPING:
            suggestions.extend(
                AdaptiveLogicService._generate_grouping_suggestions(profile)
            )

        # Filter by minimum confidence
        suggestions = [
            s for s in suggestions
            if s.confidence >= AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE
        ]

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        # Limit total suggestions
        suggestions = suggestions[:AdaptiveLogicService.MAX_TOTAL_SUGGESTIONS]

        logger.info(f"Generated {len(suggestions)} suggestions for user {user_id}")
        return suggestions

    @staticmethod
    def _generate_peak_hour_suggestions(profile: UserBehaviorProfile) -> List[Suggestion]:
        """
        Generate suggestions based on peak productivity hours.

        Examples:
        - "You're most productive at 9 AM - schedule important tasks then"
        - "Your productivity peaks between 2-4 PM"
        """
        suggestions = []

        try:
            peak_hours = json.loads(profile.peak_hours) if profile.peak_hours != "{}" else {}
        except json.JSONDecodeError:
            peak_hours = {}

        if not peak_hours:
            return suggestions

        # Sort hours by score
        sorted_hours = sorted(peak_hours.items(), key=lambda x: x[1], reverse=True)

        # Top 3 productive hours
        top_hours = sorted_hours[:3]

        if not top_hours:
            return suggestions

        # Calculate confidence based on score distribution
        top_score = top_hours[0][1]
        total_score = sum(score for _, score in peak_hours.items())

        if total_score == 0:
            return suggestions

        # Confidence = top_score / total_score (normalized)
        confidence = min(1.0, top_score / total_score * 3)  # *3 to boost confidence

        # Generate suggestion for top hour
        top_hour = int(top_hours[0][0])
        hour_12h = top_hour % 12 or 12
        am_pm = "AM" if top_hour < 12 else "PM"

        suggestion = Suggestion(
            suggestion_type=SuggestionType.PEAK_HOUR,
            title=f"Peak productivity at {hour_12h} {am_pm}",
            description=f"You complete most tasks around {hour_12h} {am_pm}. Schedule important work during this time.",
            confidence=confidence,
            reasoning=f"Based on {profile.data_points_collected} completed tasks, you're most productive at this hour.",
            metadata={
                "hour": top_hour,
                "score": top_score,
                "top_3_hours": [int(h) for h, _ in top_hours]
            }
        )
        suggestions.append(suggestion)

        # If there's a clear 2-3 hour window
        if len(top_hours) >= 3:
            hour_range = [int(h) for h, _ in top_hours]
            if max(hour_range) - min(hour_range) <= 3:
                start_h = min(hour_range) % 12 or 12
                end_h = (max(hour_range) + 1) % 12 or 12
                start_ampm = "AM" if min(hour_range) < 12 else "PM"
                end_ampm = "AM" if (max(hour_range) + 1) < 12 else "PM"

                suggestion = Suggestion(
                    suggestion_type=SuggestionType.PEAK_HOUR,
                    title=f"Productive window: {start_h} {start_ampm} - {end_h} {end_ampm}",
                    description=f"You have a consistent productivity window. Block this time for deep work.",
                    confidence=confidence * 0.9,  # Slightly lower confidence
                    reasoning=f"Your top 3 productive hours cluster together.",
                    metadata={
                        "hour_range": hour_range,
                        "window_size": max(hour_range) - min(hour_range) + 1
                    }
                )
                suggestions.append(suggestion)

        return suggestions[:AdaptiveLogicService.MAX_SUGGESTIONS_PER_TYPE]

    @staticmethod
    def _generate_type_timing_suggestions(profile: UserBehaviorProfile) -> List[Suggestion]:
        """
        Generate suggestions based on task type timing patterns.

        Examples:
        - "You usually work on coding tasks in the morning"
        - "Schedule meetings for afternoons - that's when you handle them"
        """
        suggestions = []

        try:
            type_timing = json.loads(profile.type_timing_patterns) if profile.type_timing_patterns != "{}" else {}
        except json.JSONDecodeError:
            type_timing = {}

        if not type_timing:
            return suggestions

        # For each task type, find preferred hour
        for task_type_hash, hour_frequencies in type_timing.items():
            if not hour_frequencies:
                continue

            # Find hour with highest frequency
            sorted_hours = sorted(hour_frequencies.items(), key=lambda x: x[1], reverse=True)
            preferred_hour = int(sorted_hours[0][0])
            max_frequency = sorted_hours[0][1]
            total_frequency = sum(hour_frequencies.values())

            if total_frequency < 3:  # Need at least 3 occurrences
                continue

            # Confidence based on frequency concentration
            confidence = min(1.0, max_frequency / total_frequency * 2)

            if confidence < AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE:
                continue

            hour_12h = preferred_hour % 12 or 12
            am_pm = "AM" if preferred_hour < 12 else "PM"
            time_of_day = "morning" if preferred_hour < 12 else "afternoon" if preferred_hour < 18 else "evening"

            suggestion = Suggestion(
                suggestion_type=SuggestionType.TYPE_TIMING,
                title=f"Schedule similar tasks in the {time_of_day}",
                description=f"You typically work on this type of task around {hour_12h} {am_pm}.",
                confidence=confidence,
                reasoning=f"Based on {total_frequency} similar tasks, you prefer this time slot.",
                metadata={
                    "task_type_hash": task_type_hash,
                    "preferred_hour": preferred_hour,
                    "frequency": max_frequency,
                    "time_of_day": time_of_day
                }
            )
            suggestions.append(suggestion)

        return suggestions[:AdaptiveLogicService.MAX_SUGGESTIONS_PER_TYPE]

    @staticmethod
    def _generate_priority_suggestions(profile: UserBehaviorProfile) -> List[Suggestion]:
        """
        Generate suggestions based on priority adjustment patterns.

        Examples:
        - "You often upgrade low priority tasks - consider starting higher"
        - "Tasks marked medium rarely change - your initial priority is accurate"
        """
        suggestions = []

        try:
            priority_patterns = json.loads(profile.priority_adjustment_patterns) if profile.priority_adjustment_patterns != "{}" else {}
        except json.JSONDecodeError:
            priority_patterns = {}

        if not priority_patterns:
            return suggestions

        # Analyze common priority changes
        for from_priority, to_priorities in priority_patterns.items():
            if not to_priorities:
                continue

            # Find most common change
            sorted_changes = sorted(to_priorities.items(), key=lambda x: x[1], reverse=True)
            most_common_to = sorted_changes[0][0]
            change_count = sorted_changes[0][1]

            if change_count < 3:  # Need at least 3 occurrences
                continue

            # Confidence based on frequency
            total_changes = sum(to_priorities.values())
            confidence = min(1.0, change_count / total_changes)

            if confidence < AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE:
                continue

            # Generate appropriate suggestion
            if from_priority == "low" and most_common_to == "high":
                suggestion = Suggestion(
                    suggestion_type=SuggestionType.PRIORITY_ADJUSTMENT,
                    title="Consider starting with higher priority",
                    description=f"You frequently upgrade tasks from low to high priority. Starting higher might better reflect their importance.",
                    confidence=confidence,
                    reasoning=f"You've changed {change_count} tasks from low to high priority.",
                    metadata={
                        "from_priority": from_priority,
                        "to_priority": most_common_to,
                        "frequency": change_count
                    }
                )
                suggestions.append(suggestion)

            elif from_priority == "medium" and most_common_to == "high":
                suggestion = Suggestion(
                    suggestion_type=SuggestionType.PRIORITY_ADJUSTMENT,
                    title="Medium tasks often become urgent",
                    description=f"Tasks you mark as medium priority often get upgraded. Consider starting at high priority for time-sensitive work.",
                    confidence=confidence,
                    reasoning=f"You've upgraded {change_count} medium tasks to high priority.",
                    metadata={
                        "from_priority": from_priority,
                        "to_priority": most_common_to,
                        "frequency": change_count
                    }
                )
                suggestions.append(suggestion)

        return suggestions[:AdaptiveLogicService.MAX_SUGGESTIONS_PER_TYPE]

    @staticmethod
    def _generate_grouping_suggestions(profile: UserBehaviorProfile) -> List[Suggestion]:
        """
        Generate suggestions based on task grouping patterns.

        Examples:
        - "You often work on Task A and Task B together - batch similar work"
        - "Group related tasks to maintain focus"
        """
        suggestions = []

        try:
            grouping_patterns = json.loads(profile.grouping_patterns) if profile.grouping_patterns != "{}" else {}
        except json.JSONDecodeError:
            grouping_patterns = {}

        if not grouping_patterns:
            return suggestions

        # Find strongest grouping patterns
        grouping_strength = []
        for task_type, related_types in grouping_patterns.items():
            if not related_types:
                continue

            # Number of related tasks = strength indicator
            strength = len(related_types)
            grouping_strength.append((task_type, related_types, strength))

        # Sort by strength
        grouping_strength.sort(key=lambda x: x[2], reverse=True)

        # Generate suggestions for top groupings
        for task_type, related_types, strength in grouping_strength[:3]:
            if strength < 2:  # Need at least 2 related tasks
                continue

            # Confidence based on number of related tasks
            confidence = min(1.0, strength / 5)  # Max confidence at 5+ related tasks

            if confidence < AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE:
                continue

            suggestion = Suggestion(
                suggestion_type=SuggestionType.TASK_GROUPING,
                title=f"Batch similar tasks together",
                description=f"You often work on {strength} related task types together. Grouping them saves context-switching time.",
                confidence=confidence,
                reasoning=f"You've worked on these task types in the same sessions {strength} times.",
                metadata={
                    "anchor_task_type": task_type,
                    "related_types": related_types,
                    "group_size": strength
                }
            )
            suggestions.append(suggestion)

        return suggestions[:AdaptiveLogicService.MAX_SUGGESTIONS_PER_TYPE]

    @staticmethod
    def rank_suggestions_by_confidence(
        suggestions: List[Suggestion]
    ) -> Dict[str, List[Suggestion]]:
        """
        Rank suggestions into confidence tiers.

        Returns:
            Dict with keys: "high_confidence", "medium_confidence", "low_confidence"
        """
        high = []
        medium = []
        low = []

        for suggestion in suggestions:
            if suggestion.confidence >= AdaptiveLogicService.HIGH_CONFIDENCE_THRESHOLD:
                high.append(suggestion)
            elif suggestion.confidence >= AdaptiveLogicService.MIN_SUGGESTION_CONFIDENCE:
                medium.append(suggestion)
            else:
                low.append(suggestion)

        return {
            "high_confidence": high,
            "medium_confidence": medium,
            "low_confidence": low
        }

    @staticmethod
    def generate_time_slot_recommendations(
        user_id: str,
        session: Session,
        target_hour: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate time slot recommendations for scheduling.

        Args:
            user_id: User UUID
            session: Database session
            target_hour: Optional specific hour to analyze (0-23)

        Returns:
            List of time slot recommendations with suitability scores
        """
        import uuid
        profile = session.exec(
            select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == uuid.UUID(user_id))
        ).first()

        if not profile:
            return []

        try:
            peak_hours = json.loads(profile.peak_hours) if profile.peak_hours != "{}" else {}
        except json.JSONDecodeError:
            peak_hours = {}

        if not peak_hours:
            return []

        recommendations = []

        # If target hour specified, analyze that hour
        if target_hour is not None:
            score = peak_hours.get(str(target_hour), 0)
            max_score = max(peak_hours.values()) if peak_hours else 1
            suitability = score / max_score if max_score > 0 else 0

            return [{
                "hour": target_hour,
                "suitability_score": round(suitability, 2),
                "recommendation": "High" if suitability >= 0.75 else "Medium" if suitability >= 0.5 else "Low",
                "reasoning": f"Your productivity at this hour is {int(suitability * 100)}% of your peak."
            }]

        # Generate recommendations for all hours
        max_score = max(peak_hours.values())

        for hour_str, score in peak_hours.items():
            hour = int(hour_str)
            suitability = score / max_score if max_score > 0 else 0

            hour_12h = hour % 12 or 12
            am_pm = "AM" if hour < 12 else "PM"

            recommendations.append({
                "hour": hour,
                "time_display": f"{hour_12h} {am_pm}",
                "suitability_score": round(suitability, 2),
                "recommendation": "High" if suitability >= 0.75 else "Medium" if suitability >= 0.5 else "Low",
                "reasoning": f"{int(suitability * 100)}% of peak productivity"
            })

        # Sort by suitability (highest first)
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

        return recommendations
