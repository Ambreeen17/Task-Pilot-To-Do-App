"""
Signal Decay and Forgetting Policy - Phase 5 Agent 1 (Tasks 1.3 & 1.4)

Implements time-based decay of learned patterns and forgetting rules to ensure:
1. Recent behavior is weighted more heavily than old behavior
2. Stale patterns are automatically forgotten
3. Users can start fresh without old patterns interfering

Reference: ADR-002 Pattern Analysis and Confidence Scoring System
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field


class DecayProfile(str, Enum):
    """Decay rate profiles for different types of signals"""
    FAST = "fast"        # Decays quickly (daily habits)
    MEDIUM = "medium"    # Standard decay (weekly patterns)
    SLOW = "slow"        # Decays slowly (long-term preferences)


class ForgettingTrigger(str, Enum):
    """Events that trigger pattern forgetting"""
    AGE_THRESHOLD = "age_threshold"          # Pattern too old
    INACTIVITY = "inactivity"                # No recent data points
    LOW_CONFIDENCE = "low_confidence"        # Confidence dropped below minimum
    USER_RESET = "user_reset"                # User manually reset
    PATTERN_CONFLICT = "pattern_conflict"    # New pattern contradicts old


class DecayConfig(BaseModel):
    """Configuration for signal decay behavior"""
    profile: DecayProfile
    half_life_days: int = Field(
        description="Days until signal weight drops to 50%"
    )
    min_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Minimum confidence before pattern is forgotten"
    )
    max_age_days: int = Field(
        description="Maximum age before automatic forgetting"
    )


class DecayPolicy:
    """
    Time-based decay policy for learned patterns.

    Decay Principle: Recent behavior is more indicative of current preferences
    than old behavior. Patterns should decay over time unless reinforced.
    """

    # Decay configurations by time period
    DECAY_CONFIGS: Dict[str, DecayConfig] = {
        "peak_hours": DecayConfig(
            profile=DecayProfile.MEDIUM,
            half_life_days=30,
            min_confidence=0.50,
            max_age_days=90
        ),
        "type_timing": DecayConfig(
            profile=DecayProfile.MEDIUM,
            half_life_days=30,
            min_confidence=0.50,
            max_age_days=90
        ),
        "priority_adjustment": DecayConfig(
            profile=DecayProfile.FAST,
            half_life_days=14,
            min_confidence=0.55,
            max_age_days=60
        ),
        "grouping": DecayConfig(
            profile=DecayProfile.SLOW,
            half_life_days=60,
            min_confidence=0.45,
            max_age_days=120
        ),
    }

    # Exponential decay weights by age range
    DECAY_WEIGHTS: Dict[str, float] = {
        "0-30": 1.0,    # Last 30 days: full weight
        "31-60": 0.7,   # 31-60 days: 70% weight
        "61-90": 0.4,   # 61-90 days: 40% weight
        "91+": 0.2      # 91+ days: 20% weight
    }

    @classmethod
    def calculate_decay_weight(cls, days_old: int, pattern_type: str) -> float:
        """
        Calculate decay weight for a signal based on its age.

        Uses exponential decay formula:
        weight = 2^(-days_old / half_life_days)

        Args:
            days_old: Age of signal in days
            pattern_type: Type of pattern (e.g., "peak_hours", "type_timing")

        Returns:
            Decay weight between 0.0 and 1.0
        """
        if pattern_type not in cls.DECAY_CONFIGS:
            # Default to medium decay if unknown
            half_life = 30
        else:
            half_life = cls.DECAY_CONFIGS[pattern_type].half_life_days

        # Exponential decay: weight = 2^(-days_old / half_life)
        decay_weight = 2 ** (-days_old / half_life)

        return max(0.0, min(1.0, decay_weight))

    @classmethod
    def get_age_bucket_weight(cls, days_old: int) -> float:
        """
        Get simplified bucket-based decay weight.

        Used for simpler decay calculations where exact exponential decay
        is not required.

        Args:
            days_old: Age of signal in days

        Returns:
            Bucket weight (1.0, 0.7, 0.4, or 0.2)
        """
        if days_old <= 30:
            return cls.DECAY_WEIGHTS["0-30"]
        elif days_old <= 60:
            return cls.DECAY_WEIGHTS["31-60"]
        elif days_old <= 90:
            return cls.DECAY_WEIGHTS["61-90"]
        else:
            return cls.DECAY_WEIGHTS["91+"]

    @classmethod
    def should_forget_pattern(
        cls,
        pattern_type: str,
        last_updated: datetime,
        confidence_score: float,
        data_points_count: int
    ) -> tuple[bool, Optional[ForgettingTrigger]]:
        """
        Determine if a pattern should be forgotten based on forgetting rules.

        Forgetting Rules:
        1. Age Threshold: Pattern older than max_age_days
        2. Inactivity: No new data points in 60 days
        3. Low Confidence: Confidence dropped below min_confidence
        4. Insufficient Data: Less than 3 data points

        Args:
            pattern_type: Type of pattern
            last_updated: When pattern was last updated
            confidence_score: Current confidence score (0-1)
            data_points_count: Number of data points supporting pattern

        Returns:
            Tuple of (should_forget: bool, trigger: Optional[ForgettingTrigger])
        """
        if pattern_type not in cls.DECAY_CONFIGS:
            return False, None

        config = cls.DECAY_CONFIGS[pattern_type]
        now = datetime.utcnow()
        days_old = (now - last_updated).days

        # Rule 1: Age Threshold
        if days_old > config.max_age_days:
            return True, ForgettingTrigger.AGE_THRESHOLD

        # Rule 2: Inactivity (no updates in 60 days)
        if days_old > 60:
            return True, ForgettingTrigger.INACTIVITY

        # Rule 3: Low Confidence
        if confidence_score < config.min_confidence:
            return True, ForgettingTrigger.LOW_CONFIDENCE

        # Rule 4: Insufficient Data
        if data_points_count < 3:
            return True, ForgettingTrigger.LOW_CONFIDENCE

        return False, None

    @classmethod
    def calculate_recency_weight(cls, timestamp: datetime) -> float:
        """
        Calculate recency weight for confidence scoring.

        More recent events contribute more to confidence score.
        Uses exponential decay with 30-day half-life.

        Args:
            timestamp: When event occurred

        Returns:
            Recency weight (0.0 to 1.0)
        """
        days_old = (datetime.utcnow() - timestamp).days
        return cls.calculate_decay_weight(days_old, "peak_hours")

    @classmethod
    def filter_recent_events(
        cls,
        events: List[Dict],
        timestamp_field: str = "timestamp",
        max_age_days: int = 90
    ) -> List[Dict]:
        """
        Filter events to only include those within max_age_days.

        Used to exclude stale data from pattern analysis.

        Args:
            events: List of event dictionaries
            timestamp_field: Name of timestamp field in events
            max_age_days: Maximum age in days

        Returns:
            Filtered list of recent events
        """
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        return [
            event for event in events
            if event.get(timestamp_field, datetime.min) > cutoff
        ]

    @classmethod
    def apply_decay_to_pattern_scores(
        cls,
        pattern_scores: Dict[str, float],
        last_updated: datetime,
        pattern_type: str
    ) -> Dict[str, float]:
        """
        Apply decay weights to pattern scores based on age.

        Args:
            pattern_scores: Dictionary of pattern scores (e.g., {hour: score})
            last_updated: When patterns were last updated
            pattern_type: Type of pattern for decay calculation

        Returns:
            Decayed pattern scores
        """
        days_old = (datetime.utcnow() - last_updated).days
        decay_weight = cls.calculate_decay_weight(days_old, pattern_type)

        return {
            key: score * decay_weight
            for key, score in pattern_scores.items()
        }

    @classmethod
    def get_forgetting_config(cls, pattern_type: str) -> DecayConfig:
        """Get decay/forgetting configuration for a pattern type"""
        return cls.DECAY_CONFIGS.get(
            pattern_type,
            DecayConfig(
                profile=DecayProfile.MEDIUM,
                half_life_days=30,
                min_confidence=0.50,
                max_age_days=90
            )
        )


class ForgettingPolicy:
    """
    Pattern forgetting policy for maintaining data quality.

    Forgetting Principle: Old, low-confidence, or contradictory patterns
    should be removed to prevent stale suggestions.
    """

    # Minimum data points required to establish a pattern
    MIN_DATA_POINTS = 3

    # Inactivity period before pattern is forgotten (days)
    INACTIVITY_THRESHOLD_DAYS = 60

    # Confidence threshold for pattern retention
    MIN_CONFIDENCE_THRESHOLD = 0.45

    @classmethod
    def should_retain_pattern(
        cls,
        pattern_type: str,
        confidence: float,
        data_points: int,
        last_updated: datetime
    ) -> bool:
        """
        Determine if a pattern should be retained (inverse of should_forget).

        Args:
            pattern_type: Type of pattern
            confidence: Current confidence score
            data_points: Number of supporting data points
            last_updated: Last update timestamp

        Returns:
            True if pattern should be retained, False if forgotten
        """
        should_forget, _ = DecayPolicy.should_forget_pattern(
            pattern_type, last_updated, confidence, data_points
        )
        return not should_forget

    @classmethod
    def prune_old_patterns(
        cls,
        patterns: Dict[str, Dict],
        current_time: datetime = None
    ) -> Dict[str, Dict]:
        """
        Remove patterns that should be forgotten based on forgetting rules.

        Args:
            patterns: Dictionary of pattern_type -> pattern_data
            current_time: Current time (for testing)

        Returns:
            Pruned patterns dictionary
        """
        if current_time is None:
            current_time = datetime.utcnow()

        pruned = {}
        for pattern_type, pattern_data in patterns.items():
            # Check if pattern should be retained
            should_retain = cls.should_retain_pattern(
                pattern_type=pattern_type,
                confidence=pattern_data.get("confidence", 0.0),
                data_points=pattern_data.get("data_points", 0),
                last_updated=pattern_data.get("last_updated", current_time)
            )

            if should_retain:
                pruned[pattern_type] = pattern_data

        return pruned

    @classmethod
    def get_forgetting_explanation(cls, trigger: ForgettingTrigger) -> str:
        """Get human-readable explanation for why pattern was forgotten"""
        explanations = {
            ForgettingTrigger.AGE_THRESHOLD: "Pattern is too old and no longer relevant",
            ForgettingTrigger.INACTIVITY: "No recent activity to support this pattern",
            ForgettingTrigger.LOW_CONFIDENCE: "Pattern confidence dropped below minimum threshold",
            ForgettingTrigger.USER_RESET: "You manually reset your learning data",
            ForgettingTrigger.PATTERN_CONFLICT: "New behavior contradicts this pattern"
        }
        return explanations.get(trigger, "Pattern no longer relevant")
