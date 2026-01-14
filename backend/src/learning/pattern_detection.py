"""
Pattern Detection Service - Phase 5 Agent 3 (Tasks 3.3-3.7)

Analyzes captured behavioral events to detect patterns:
- Peak productivity hours
- Task type timing preferences
- Priority adjustment patterns
- Task grouping behaviors

Reference: ADR-002 Pattern Analysis and Confidence Scoring System
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
from sqlmodel import Session, select

from .decay_policy import DecayPolicy
from .schemas import (
    PeakHoursPattern,
    TaskTimingPattern,
    PriorityAdjustmentPattern,
    GroupingPattern
)


class PatternDetectionService:
    """
    Service for detecting behavioral patterns from captured events.

    Pattern Detection Principle: Patterns must be statistically significant
    (≥3 occurrences) and have sufficient confidence (≥0.40) to be considered.
    """

    # Minimum data points required for pattern detection
    MIN_PATTERN_OCCURRENCES = 3
    MIN_CONFIDENCE_THRESHOLD = 0.40

    @staticmethod
    def detect_peak_hours(
        events: List,
        min_occurrences: int = MIN_PATTERN_OCCURRENCES
    ) -> Tuple[Dict[int, float], float, int]:
        """
        Detect peak productivity hours from task completion events.

        Analyzes which hours of day user most frequently completes tasks.
        Applies decay weights to prioritize recent behavior.

        Args:
            events: List of BehavioralEvent objects (task_completed type)
            min_occurrences: Minimum occurrences to consider a pattern

        Returns:
            Tuple of (hour_scores: Dict[hour, score], confidence: float, data_points: int)

        Algorithm:
        1. Count completions per hour with decay weights
        2. Calculate frequency weights (0-1 scale)
        3. Calculate recency weights (recent events weighted higher)
        4. Calculate consistency (low variance = higher confidence)
        5. Combine: confidence = (frequency * 0.4) + (recency * 0.3) + (consistency * 0.3)
        """
        if not events or len(events) < min_occurrences:
            return {}, 0.0, 0

        # Count occurrences per hour with decay weights
        hour_counts = defaultdict(float)
        hour_timestamps = defaultdict(list)

        for event in events:
            # Apply decay weight based on event age
            days_old = (datetime.utcnow() - event.timestamp).days
            decay_weight = DecayPolicy.calculate_decay_weight(days_old, "peak_hours")

            hour_counts[event.hour_of_day] += decay_weight
            hour_timestamps[event.hour_of_day].append(event.timestamp)

        # Filter hours with insufficient occurrences
        significant_hours = {
            hour: count for hour, count in hour_counts.items()
            if len(hour_timestamps[hour]) >= min_occurrences
        }

        if not significant_hours:
            return {}, 0.0, 0

        # Normalize scores to 0-1 scale (frequency weight)
        max_count = max(significant_hours.values())
        hour_scores = {
            hour: count / max_count
            for hour, count in significant_hours.items()
        }

        # Calculate recency weight (how recent is the pattern?)
        total_recency = 0.0
        for hour in significant_hours:
            timestamps = hour_timestamps[hour]
            most_recent = max(timestamps)
            recency_weight = DecayPolicy.calculate_recency_weight(most_recent)
            total_recency += recency_weight

        avg_recency = total_recency / len(significant_hours)

        # Calculate consistency weight (low variance = more consistent)
        counts = list(significant_hours.values())
        if len(counts) > 1:
            mean_count = sum(counts) / len(counts)
            variance = sum((c - mean_count) ** 2 for c in counts) / len(counts)
            consistency_weight = 1.0 / (1.0 + variance)  # Lower variance = higher consistency
        else:
            consistency_weight = 1.0

        # Confidence formula: (frequency * 0.4) + (recency * 0.3) + (consistency * 0.3)
        confidence = (
            (max(hour_scores.values()) * 0.4) +
            (avg_recency * 0.3) +
            (consistency_weight * 0.3)
        )

        return hour_scores, confidence, len(events)

    @staticmethod
    def detect_type_timing_patterns(
        events: List,
        min_occurrences: int = MIN_PATTERN_OCCURRENCES
    ) -> Tuple[Dict[str, Dict[int, int]], float, int]:
        """
        Detect task type timing patterns.

        Identifies which hours are preferred for specific task types.

        Args:
            events: List of BehavioralEvent objects
            min_occurrences: Minimum occurrences per type

        Returns:
            Tuple of (patterns: Dict[type_hash, {hour: frequency}], confidence: float, data_points: int)

        Example:
            {
                "abc123": {9: 5, 14: 3},  # This task type done 5x at 9am, 3x at 2pm
                "def456": {10: 4, 15: 2}
            }
        """
        if not events or len(events) < min_occurrences:
            return {}, 0.0, 0

        # Group by task type hash and hour
        type_timing = defaultdict(lambda: defaultdict(int))
        type_timestamps = defaultdict(list)

        for event in events:
            days_old = (datetime.utcnow() - event.timestamp).days
            decay_weight = DecayPolicy.calculate_decay_weight(days_old, "type_timing")

            type_timing[event.task_type_hash][event.hour_of_day] += decay_weight
            type_timestamps[event.task_type_hash].append(event.timestamp)

        # Filter types with insufficient occurrences
        significant_patterns = {}
        for task_type, hours in type_timing.items():
            if len(type_timestamps[task_type]) >= min_occurrences:
                # Round decay-weighted counts to integers
                significant_patterns[task_type] = {
                    hour: int(count) for hour, count in hours.items()
                }

        if not significant_patterns:
            return {}, 0.0, 0

        # Calculate confidence based on pattern strength
        total_types = len(significant_patterns)
        avg_occurrences = sum(
            sum(hours.values()) for hours in significant_patterns.values()
        ) / total_types

        # More occurrences and more types = higher confidence
        frequency_weight = min(1.0, avg_occurrences / 10)  # Cap at 10 occurrences
        diversity_weight = min(1.0, total_types / 5)  # Cap at 5 types

        confidence = (frequency_weight * 0.6) + (diversity_weight * 0.4)

        return significant_patterns, confidence, len(events)

    @staticmethod
    def detect_priority_adjustment_patterns(
        events: List,
        min_occurrences: int = MIN_PATTERN_OCCURRENCES
    ) -> Tuple[Dict[str, Dict[str, int]], float, int]:
        """
        Detect priority adjustment patterns.

        Identifies common priority changes (e.g., low → high in mornings).

        Args:
            events: List of BehavioralEvent objects (priority_changed type)
            min_occurrences: Minimum occurrences

        Returns:
            Tuple of (patterns: Dict[from_priority, {to_priority: frequency}], confidence: float, data_points: int)

        Example:
            {
                "low": {"high": 5, "medium": 2},  # low→high 5x, low→medium 2x
                "medium": {"high": 3}
            }
        """
        if not events or len(events) < min_occurrences:
            return {}, 0.0, 0

        # Filter priority change events
        priority_events = [e for e in events if e.event_type == "priority_changed"]
        if not priority_events:
            return {}, 0.0, 0

        # Count priority change patterns with decay
        priority_flows = defaultdict(lambda: defaultdict(float))

        for event in priority_events:
            if event.from_priority and event.to_priority:
                days_old = (datetime.utcnow() - event.timestamp).days
                decay_weight = DecayPolicy.calculate_decay_weight(days_old, "priority_adjustment")

                priority_flows[event.from_priority][event.to_priority] += decay_weight

        # Convert to integers
        significant_flows = {}
        for from_pri, to_pris in priority_flows.items():
            significant_flows[from_pri] = {
                to_pri: int(count) for to_pri, count in to_pris.items()
                if count >= min_occurrences
            }

        # Remove empty entries
        significant_flows = {k: v for k, v in significant_flows.items() if v}

        if not significant_flows:
            return {}, 0.0, 0

        # Calculate confidence based on pattern clarity
        total_changes = sum(
            sum(to_pris.values()) for to_pris in significant_flows.values()
        )

        frequency_weight = min(1.0, total_changes / 10)
        confidence = frequency_weight * 0.8  # High weight on frequency for priority patterns

        return significant_flows, confidence, len(priority_events)

    @staticmethod
    def detect_grouping_patterns(
        events: List,
        min_occurrences: int = MIN_PATTERN_OCCURRENCES
    ) -> Tuple[Dict[str, List[str]], float, int]:
        """
        Detect task grouping patterns.

        Identifies which task types are frequently worked on together in same session.

        Args:
            events: List of BehavioralEvent objects (task_grouped type)
            min_occurrences: Minimum co-occurrences

        Returns:
            Tuple of (patterns: Dict[type_hash, [related_type_hashes]], confidence: float, data_points: int)

        Example:
            {
                "abc123": ["def456", "ghi789"],  # abc123 often grouped with def456, ghi789
                "def456": ["abc123"]
            }
        """
        if not events or len(events) < min_occurrences:
            return {}, 0.0, 0

        # Group events by session_id
        sessions = defaultdict(set)
        for event in events:
            if event.session_id:
                sessions[event.session_id].add(event.task_type_hash)

        # Find co-occurrence patterns
        grouping_patterns = defaultdict(lambda: defaultdict(int))

        for session_types in sessions.values():
            session_types_list = list(session_types)
            # For each type in session, track what it was grouped with
            for i, type1 in enumerate(session_types_list):
                for type2 in session_types_list[i+1:]:
                    grouping_patterns[type1][type2] += 1
                    grouping_patterns[type2][type1] += 1

        # Filter by minimum occurrences
        significant_patterns = {}
        for type_hash, related_types in grouping_patterns.items():
            related_list = [
                related_type for related_type, count in related_types.items()
                if count >= min_occurrences
            ]
            if related_list:
                significant_patterns[type_hash] = related_list

        if not significant_patterns:
            return {}, 0.0, 0

        # Calculate confidence based on grouping frequency
        total_groups = len(sessions)
        avg_group_size = sum(len(types) for types in sessions.values()) / total_groups

        frequency_weight = min(1.0, total_groups / 10)
        size_weight = min(1.0, avg_group_size / 3)  # Groups of 3+ tasks

        confidence = (frequency_weight * 0.5) + (size_weight * 0.5)

        return significant_patterns, confidence, len(events)

    @staticmethod
    def calculate_pattern_confidence(
        data_points: int,
        recency_weight: float,
        consistency_weight: float
    ) -> float:
        """
        Calculate overall pattern confidence score.

        Confidence Formula (from ADR-002):
        confidence = (frequency_weight * 0.4) + (recency_weight * 0.3) + (consistency_weight * 0.3)

        Args:
            data_points: Number of events supporting pattern
            recency_weight: How recent the pattern is (0-1)
            consistency_weight: How consistent the pattern is (0-1)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Frequency weight based on data points (more data = higher confidence)
        frequency_weight = min(1.0, data_points / 20)  # 20 events = max frequency weight

        confidence = (
            (frequency_weight * 0.4) +
            (recency_weight * 0.3) +
            (consistency_weight * 0.3)
        )

        return max(0.0, min(1.0, confidence))

    @staticmethod
    def should_suggest_pattern(confidence: float, threshold: float = 0.60) -> bool:
        """
        Determine if pattern confidence is high enough to generate suggestions.

        Thresholds (from POLICY.md):
        - Pattern detection: ≥0.40
        - Suggestion generation: ≥0.60
        - High confidence: ≥0.75

        Args:
            confidence: Pattern confidence score
            threshold: Minimum threshold (default: 0.60 for suggestions)

        Returns:
            True if pattern should be used for suggestions
        """
        return confidence >= threshold
