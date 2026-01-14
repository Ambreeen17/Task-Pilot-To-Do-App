"""
Batch Learning Job - Phase 5 Agent 3 (Task 3.5)

Runs pattern detection on all user behavioral events in batch.
Scheduled to run daily at 2 AM to update learned patterns.

Performance Target: <30 seconds per user

Reference: ADR-002 Pattern Analysis and Confidence Scoring System
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import json
import logging

from ..models.behavioral_event import BehavioralEvent, UserBehaviorProfile
from ..models.preferences import UserPreferences
from .pattern_detection import PatternDetectionService
from .decay_policy import DecayPolicy, ForgettingPolicy

logger = logging.getLogger(__name__)


class BatchLearningJob:
    """
    Batch job for updating user behavioral patterns.

    Runs daily to:
    1. Load recent behavioral events (last 90 days)
    2. Detect patterns using PatternDetectionService
    3. Update UserBehaviorProfile with new patterns
    4. Prune stale patterns using ForgettingPolicy
    """

    # Configuration
    MAX_EVENT_AGE_DAYS = 90  # Only analyze recent events
    BATCH_SIZE = 100  # Process 100 users at a time
    MAX_EXECUTION_TIME_PER_USER = 30  # seconds

    @staticmethod
    def run_for_all_users(session: Session) -> Dict[str, Any]:
        """
        Run batch learning for all users with learning enabled.

        Returns:
            Summary statistics: users processed, patterns updated, errors
        """
        logger.info("Starting batch learning job")
        start_time = datetime.utcnow()

        # Get all users with learning enabled
        users_with_learning = session.exec(
            select(UserPreferences).where(
                UserPreferences.learning_enabled == True,
                UserPreferences.learning_paused == False
            )
        ).all()

        stats = {
            "users_processed": 0,
            "users_skipped": 0,
            "patterns_updated": 0,
            "patterns_forgotten": 0,
            "errors": 0,
            "execution_time_seconds": 0
        }

        for prefs in users_with_learning:
            try:
                user_stats = BatchLearningJob.run_for_user(prefs.user_id, session)
                stats["users_processed"] += 1
                stats["patterns_updated"] += user_stats["patterns_updated"]
                stats["patterns_forgotten"] += user_stats["patterns_forgotten"]
            except Exception as e:
                logger.error(f"Error processing user {prefs.user_id}: {e}")
                stats["errors"] += 1

        end_time = datetime.utcnow()
        stats["execution_time_seconds"] = (end_time - start_time).total_seconds()

        logger.info(f"Batch learning job complete: {stats}")
        return stats

    @staticmethod
    def run_for_user(user_id: str, session: Session) -> Dict[str, Any]:
        """
        Run pattern detection for a single user.

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            User-specific statistics
        """
        import uuid

        user_start = datetime.utcnow()

        # Load recent events (last 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=BatchLearningJob.MAX_EVENT_AGE_DAYS)
        events = session.exec(
            select(BehavioralEvent).where(
                BehavioralEvent.user_id == uuid.UUID(user_id),
                BehavioralEvent.timestamp >= cutoff_date
            )
        ).all()

        if not events:
            logger.debug(f"No recent events for user {user_id}")
            return {"patterns_updated": 0, "patterns_forgotten": 0}

        # Get or create behavior profile
        profile = session.exec(
            select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == uuid.UUID(user_id))
        ).first()

        if not profile:
            profile = UserBehaviorProfile(
                user_id=uuid.UUID(user_id),
                learning_enabled=True
            )
            session.add(profile)

        # Detect patterns
        patterns_updated = 0

        # 1. Peak Hours Pattern
        peak_hours, peak_confidence, peak_data_points = PatternDetectionService.detect_peak_hours(events)
        if peak_hours and peak_confidence >= PatternDetectionService.MIN_CONFIDENCE_THRESHOLD:
            profile.peak_hours = json.dumps(peak_hours)
            patterns_updated += 1
            logger.debug(f"Updated peak_hours for user {user_id}: confidence={peak_confidence:.2f}")

        # 2. Type Timing Pattern
        type_timing, timing_confidence, timing_data_points = PatternDetectionService.detect_type_timing_patterns(events)
        if type_timing and timing_confidence >= PatternDetectionService.MIN_CONFIDENCE_THRESHOLD:
            profile.type_timing_patterns = json.dumps(type_timing)
            patterns_updated += 1
            logger.debug(f"Updated type_timing for user {user_id}: confidence={timing_confidence:.2f}")

        # 3. Priority Adjustment Pattern
        priority_adj, priority_confidence, priority_data_points = PatternDetectionService.detect_priority_adjustment_patterns(events)
        if priority_adj and priority_confidence >= PatternDetectionService.MIN_CONFIDENCE_THRESHOLD:
            profile.priority_adjustment_patterns = json.dumps(priority_adj)
            patterns_updated += 1
            logger.debug(f"Updated priority_adjustment for user {user_id}: confidence={priority_confidence:.2f}")

        # 4. Grouping Pattern
        grouping, grouping_confidence, grouping_data_points = PatternDetectionService.detect_grouping_patterns(events)
        if grouping and grouping_confidence >= PatternDetectionService.MIN_CONFIDENCE_THRESHOLD:
            profile.grouping_patterns = json.dumps(grouping)
            patterns_updated += 1
            logger.debug(f"Updated grouping for user {user_id}: confidence={grouping_confidence:.2f}")

        # Update metadata
        profile.data_points_collected = len(events)
        profile.last_learning_date = datetime.utcnow()

        # Prune stale patterns using ForgettingPolicy
        patterns = {
            "peak_hours": {
                "confidence": peak_confidence,
                "data_points": peak_data_points,
                "last_updated": datetime.utcnow()
            },
            "type_timing": {
                "confidence": timing_confidence,
                "data_points": timing_data_points,
                "last_updated": datetime.utcnow()
            },
            "priority_adjustment": {
                "confidence": priority_confidence,
                "data_points": priority_data_points,
                "last_updated": datetime.utcnow()
            },
            "grouping": {
                "confidence": grouping_confidence,
                "data_points": grouping_data_points,
                "last_updated": datetime.utcnow()
            }
        }

        pruned_patterns = ForgettingPolicy.prune_old_patterns(patterns)
        patterns_forgotten = len(patterns) - len(pruned_patterns)

        # Clear forgotten patterns from profile
        if "peak_hours" not in pruned_patterns:
            profile.peak_hours = "{}"
        if "type_timing" not in pruned_patterns:
            profile.type_timing_patterns = "{}"
        if "priority_adjustment" not in pruned_patterns:
            profile.priority_adjustment_patterns = "{}"
        if "grouping" not in pruned_patterns:
            profile.grouping_patterns = "{}"

        session.commit()

        user_end = datetime.utcnow()
        execution_time = (user_end - user_start).total_seconds()

        logger.info(
            f"User {user_id}: {patterns_updated} patterns updated, "
            f"{patterns_forgotten} forgotten, {execution_time:.2f}s"
        )

        return {
            "patterns_updated": patterns_updated,
            "patterns_forgotten": patterns_forgotten,
            "execution_time": execution_time
        }

    @staticmethod
    def trigger_manual_learning(user_id: str, session: Session) -> Dict[str, Any]:
        """
        Manually trigger pattern learning for a specific user.

        Useful for:
        - Testing learning system
        - Immediate pattern updates after user requests
        - On-demand pattern refresh

        Args:
            user_id: User UUID
            session: Database session

        Returns:
            Learning results and statistics
        """
        logger.info(f"Manual learning trigger for user {user_id}")
        return BatchLearningJob.run_for_user(user_id, session)

    @staticmethod
    def schedule_daily_job():
        """
        Schedule batch learning job to run daily at 2 AM.

        Implementation note: This is a placeholder for scheduling.
        In production, use:
        - APScheduler (Python)
        - Celery Beat (distributed)
        - Cloud scheduler (AWS CloudWatch Events, GCP Cloud Scheduler)
        - Kubernetes CronJob

        Example with APScheduler:
        ```python
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            BatchLearningJob.run_for_all_users,
            trigger='cron',
            hour=2,
            minute=0,
            args=[session]
        )
        scheduler.start()
        ```
        """
        logger.info("Batch learning job scheduled for daily execution at 2 AM")
        # TODO: Implement actual scheduling in production

    @staticmethod
    def get_learning_stats(session: Session) -> Dict[str, Any]:
        """
        Get overall learning system statistics.

        Returns:
            System-wide statistics for monitoring
        """
        # Count users with learning enabled
        users_with_learning = session.exec(
            select(UserPreferences).where(UserPreferences.learning_enabled == True)
        ).all()

        # Count total events
        total_events = session.exec(
            select(BehavioralEvent)
        ).all()

        # Count profiles with patterns
        profiles = session.exec(select(UserBehaviorProfile)).all()
        profiles_with_patterns = sum(
            1 for p in profiles
            if p.peak_hours != "{}" or p.type_timing_patterns != "{}"
        )

        return {
            "users_with_learning_enabled": len(users_with_learning),
            "total_behavioral_events": len(total_events),
            "profiles_with_patterns": profiles_with_patterns,
            "total_profiles": len(profiles)
        }
