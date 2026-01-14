"""
Learning API Router - Phase 5 Agent 2

Handles user consent, learning controls, and GDPR/CCPA compliance endpoints.

Critical: Learning is OPT-IN only. Users must explicitly consent before any
behavioral data collection begins.

Reference: ADR-003 User Control and Transparency Framework
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional
import json
import uuid

from ..database import get_session
from ..dependencies import get_current_user
from ..models.user import User
from ..models.preferences import UserPreferences
from ..models.behavioral_event import BehavioralEvent, UserBehaviorProfile
from ..learning.signal_policy import SignalPolicy
from ..learning.event_capture import EventCaptureService, EventCaptureError
from ..learning.batch_learning import BatchLearningJob
from ..learning.schemas import (
    LearningControlRequest,
    LearningStatusResponse,
    PrivacySummaryResponse,
    BehavioralEventCreate,
    BehavioralEventResponse,
    PriorityChangeEvent
)

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/privacy-policy", response_model=PrivacySummaryResponse)
async def get_privacy_policy():
    """
    Get privacy policy summary for learning system.

    Shows users exactly what is learned (privacy-safe metadata)
    and what is NOT learned (privacy-protected content).

    **Transparency Requirement**: Users must be able to see privacy policy
    before consenting to learning.
    """
    policy = SignalPolicy.get_privacy_summary()
    return PrivacySummaryResponse(
        learnable_signals=policy["learnable"],
        forbidden_signals=policy["forbidden"],
        privacy_guarantees=[
            "No task content, titles, or descriptions stored",
            "Only timing, frequency, and grouping patterns learned",
            "All learning is opt-in and reversible",
            "Complete data deletion available at any time",
            "GDPR Article 15 & 17 compliant"
        ]
    )


@router.get("/status", response_model=LearningStatusResponse)
async def get_learning_status(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get current learning status for authenticated user.

    Returns:
    - Whether learning is enabled
    - Number of data points collected
    - Whether patterns are ready (≥20 events)
    - Days since learning was enabled
    """
    # Get user preferences
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs:
        # Create default preferences if none exist
        prefs = UserPreferences(user_id=current_user.id)
        session.add(prefs)
        session.commit()
        session.refresh(prefs)

    # Get behavior profile (if exists)
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    # Calculate status
    data_points = profile.data_points_collected if profile else 0
    patterns_ready = data_points >= 20  # Minimum for pattern detection
    days_since_enabled = None

    if prefs.learning_consent_date:
        days_since_enabled = (datetime.utcnow() - prefs.learning_consent_date).days

    return LearningStatusResponse(
        learning_enabled=prefs.learning_enabled,
        data_points_collected=data_points,
        days_since_enabled=days_since_enabled,
        patterns_ready=patterns_ready,
        next_learning_job=None  # TODO: Add batch job scheduling
    )


@router.post("/enable")
async def enable_learning(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Enable behavioral learning for authenticated user.

    **GDPR Article 6 Compliance**: Explicit consent required before data processing.

    This endpoint:
    1. Records consent timestamp (audit trail)
    2. Enables learning (learning_enabled=true)
    3. Creates UserBehaviorProfile if not exists
    4. Returns confirmation

    **Important**: Users should see privacy policy before calling this endpoint.
    """
    # Get or create user preferences
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        session.add(prefs)

    # Check if already enabled
    if prefs.learning_enabled:
        return {
            "message": "Learning already enabled",
            "learning_enabled": True,
            "consent_date": prefs.learning_consent_date
        }

    # Enable learning and record consent
    prefs.learning_enabled = True
    prefs.learning_consent_date = datetime.utcnow()
    prefs.learning_paused = False

    # Create behavior profile if not exists
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if not profile:
        profile = UserBehaviorProfile(
            user_id=current_user.id,
            learning_enabled=True,
            learning_paused=False
        )
        session.add(profile)

    session.commit()
    session.refresh(prefs)

    return {
        "message": "Learning enabled successfully. We'll start learning from your behavior patterns.",
        "learning_enabled": True,
        "consent_date": prefs.learning_consent_date,
        "privacy_policy": "/api/learning/privacy-policy"
    }


@router.post("/disable")
async def disable_learning(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Disable behavioral learning for authenticated user.

    This endpoint:
    1. Stops all data collection immediately
    2. Existing patterns are preserved (not deleted)
    3. User can re-enable later without losing patterns

    **Note**: To completely delete all learning data, use DELETE /learning/reset
    """
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    # Disable learning
    prefs.learning_enabled = False
    prefs.learning_paused = False

    # Update profile
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if profile:
        profile.learning_enabled = False

    session.commit()

    return {
        "message": "Learning disabled. Existing patterns preserved. Use /learning/reset to delete all data.",
        "learning_enabled": False,
        "data_preserved": True
    }


@router.post("/pause")
async def pause_learning(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Temporarily pause learning without disabling it.

    Difference from disable:
    - Pause: Temporarily stop, can resume easily
    - Disable: Turn off completely, more intentional

    Pausing is useful for:
    - Vacation/time off
    - Testing different workflows
    - Temporary behavior changes
    """
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs or not prefs.learning_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Learning is not enabled. Enable learning first."
        )

    prefs.learning_paused = True

    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if profile:
        profile.learning_paused = True

    session.commit()

    return {
        "message": "Learning paused. Resume anytime with /learning/resume",
        "learning_paused": True
    }


@router.post("/resume")
async def resume_learning(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Resume learning after pausing.

    Immediately resumes data collection and pattern updates.
    """
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs or not prefs.learning_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Learning is not enabled. Enable learning first."
        )

    prefs.learning_paused = False

    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if profile:
        profile.learning_paused = False

    session.commit()

    return {
        "message": "Learning resumed successfully",
        "learning_paused": False
    }


@router.delete("/reset")
async def reset_learning_data(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Complete deletion of ALL learning data (GDPR Article 17 - Right to Erasure).

    **DANGER**: This action CANNOT be undone.

    Deletes:
    - All BehavioralEvent records
    - UserBehaviorProfile (all patterns)
    - Learning consent history

    Resets:
    - learning_enabled = false
    - learning_categories = []
    - learning_consent_date = null

    **GDPR Compliance**: Complete deletion within 24 hours (immediate in this implementation).
    """
    # Count events before deletion (for audit log)
    event_count = session.exec(
        select(BehavioralEvent).where(BehavioralEvent.user_id == current_user.id)
    ).all()
    events_deleted = len(event_count)

    # Delete all behavioral events
    for event in event_count:
        session.delete(event)

    # Delete behavior profile
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    patterns_deleted = []
    if profile:
        # Track what patterns were deleted (for transparency)
        if profile.peak_hours != "{}":
            patterns_deleted.append("peak_hours")
        if profile.type_timing_patterns != "{}":
            patterns_deleted.append("type_timing")
        if profile.priority_adjustment_patterns != "{}":
            patterns_deleted.append("priority_adjustment")
        if profile.grouping_patterns != "{}":
            patterns_deleted.append("grouping")

        session.delete(profile)

    # Reset user preferences
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if prefs:
        prefs.learning_enabled = False
        prefs.learning_paused = False
        prefs.learning_consent_date = None
        prefs.learning_categories = "[]"

    session.commit()

    return {
        "message": "All learning data deleted successfully",
        "events_deleted": events_deleted,
        "patterns_deleted": patterns_deleted,
        "learning_enabled": False,
        "confirmation": "Your behavioral learning data has been permanently removed"
    }


@router.post("/categories")
async def update_learning_categories(
    categories: List[str],
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update which pattern types user consents to learn.

    Valid categories:
    - "timing": Learn peak hours and task type timing patterns
    - "priority": Learn priority adjustment patterns
    - "grouping": Learn task grouping patterns

    **Granular Control**: Users can choose specific pattern types to enable.
    """
    # Validate categories
    valid_categories = {"timing", "priority", "grouping"}
    invalid = set(categories) - valid_categories

    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid categories: {invalid}. Valid: {valid_categories}"
        )

    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    # Update categories
    prefs.learning_categories = json.dumps(categories)
    session.commit()

    return {
        "message": "Learning categories updated",
        "categories": categories
    }


@router.post("/events/capture", response_model=BehavioralEventResponse)
async def capture_behavioral_event(
    event: BehavioralEventCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Capture a behavioral event from client.

    **Privacy-Safe Event Capture**:
    - Only metadata captured (hour, day, task_type_hash)
    - NO task content, titles, descriptions
    - Validates against signal policy before storage

    **Event Types**:
    - task_completed: User completed a task
    - priority_changed: User changed task priority
    - task_grouped: User worked on related tasks in session

    **Auto-Skipped** if learning disabled or paused.
    """
    # Check if learning is enabled
    if not EventCaptureService.should_capture_event(str(current_user.id), session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Learning is not enabled or is paused. Enable learning first."
        )

    try:
        # Create event from schema
        db_event = BehavioralEvent(
            user_id=current_user.id,
            event_type=event.event_type.value,
            hour_of_day=event.hour_of_day,
            day_of_week=event.day_of_week,
            task_type_hash=event.task_type_hash,
            session_id=event.session_id,
            timestamp=datetime.utcnow()
        )

        # Validate privacy compliance
        is_compliant, violations = EventCaptureService.validate_privacy_compliance(db_event)
        if not is_compliant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Privacy validation failed: {violations}"
            )

        # Store event
        session.add(db_event)
        session.commit()
        session.refresh(db_event)

        # Update data points counter in profile
        profile = session.exec(
            select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
        ).first()

        if profile:
            profile.data_points_collected += 1
            session.commit()

        return db_event

    except EventCaptureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/events/priority-change")
async def capture_priority_change_event(
    event: PriorityChangeEvent,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Capture priority change behavioral event.

    Records when user changes task priority (e.g., low → high).
    Used to learn priority adjustment patterns.

    **Privacy**: Only priority levels captured, NO task content.
    """
    # Check if learning is enabled
    if not EventCaptureService.should_capture_event(str(current_user.id), session):
        return {
            "message": "Learning disabled or paused. Event not captured.",
            "captured": False
        }

    try:
        # Generate task type hash from a generic identifier
        # In real implementation, client should provide generic type
        task_type_hash = EventCaptureService.hash_task_type("generic")

        db_event = BehavioralEvent(
            user_id=current_user.id,
            event_type="priority_changed",
            hour_of_day=event.hour_of_day,
            day_of_week=event.day_of_week,
            task_type_hash=task_type_hash,
            session_id=event.session_id,
            from_priority=event.from_priority,
            to_priority=event.to_priority,
            timestamp=datetime.utcnow()
        )

        # Validate privacy compliance
        is_compliant, violations = EventCaptureService.validate_privacy_compliance(db_event)
        if not is_compliant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Privacy validation failed: {violations}"
            )

        session.add(db_event)
        session.commit()

        # Update data points counter
        profile = session.exec(
            select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
        ).first()

        if profile:
            profile.data_points_collected += 1
            session.commit()

        return {
            "message": "Priority change event captured",
            "captured": True,
            "event_type": "priority_changed",
            "from_priority": event.from_priority,
            "to_priority": event.to_priority
        }

    except EventCaptureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/events/count")
async def get_event_count(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get total number of behavioral events captured for user.

    Useful for showing data collection progress:
    - "Building your profile (12/20 events needed)"
    - "156 events collected since enabling learning"
    """
    count = EventCaptureService.get_user_event_count(str(current_user.id), session)

    patterns_ready = count >= 20  # Minimum for pattern detection
    progress_percentage = min(100, int((count / 20) * 100))

    return {
        "total_events": count,
        "patterns_ready": patterns_ready,
        "progress_percentage": progress_percentage,
        "message": f"{'Patterns ready!' if patterns_ready else f'{20 - count} more events needed for patterns'}"
    }


@router.post("/patterns/refresh")
async def refresh_patterns(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Manually trigger pattern learning for current user.

    Runs pattern detection immediately instead of waiting for nightly batch job.

    **Use Cases**:
    - User wants to see patterns immediately
    - Testing learning system
    - After bulk import of historical data

    **Performance**: Usually completes in <5 seconds per user.
    """
    # Check if learning is enabled
    prefs = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not prefs or not prefs.learning_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Learning is not enabled. Enable learning first."
        )

    try:
        # Run batch learning for this user
        results = BatchLearningJob.trigger_manual_learning(str(current_user.id), session)

        return {
            "message": "Patterns refreshed successfully",
            "patterns_updated": results["patterns_updated"],
            "patterns_forgotten": results["patterns_forgotten"],
            "execution_time_seconds": results["execution_time"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern refresh failed: {str(e)}"
        )


@router.get("/patterns/view")
async def view_patterns(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    View all learned patterns for current user.

    Returns:
    - Peak hours pattern (which hours user is most productive)
    - Type timing pattern (which hours for specific task types)
    - Priority adjustment pattern (common priority changes)
    - Grouping pattern (which tasks are grouped together)

    **Transparency**: Shows exactly what the system has learned.
    """
    # Get behavior profile
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if not profile:
        return {
            "message": "No patterns yet. Enable learning and complete at least 20 tasks.",
            "patterns": {}
        }

    # Parse JSON patterns
    patterns = {
        "peak_hours": json.loads(profile.peak_hours) if profile.peak_hours != "{}" else {},
        "type_timing": json.loads(profile.type_timing_patterns) if profile.type_timing_patterns != "{}" else {},
        "priority_adjustment": json.loads(profile.priority_adjustment_patterns) if profile.priority_adjustment_patterns != "{}" else {},
        "grouping": json.loads(profile.grouping_patterns) if profile.grouping_patterns != "{}" else {},
        "metadata": {
            "data_points_collected": profile.data_points_collected,
            "last_learning_date": profile.last_learning_date,
            "model_version": profile.model_version,
            "learning_enabled": profile.learning_enabled
        }
    }

    # Count non-empty patterns
    pattern_count = sum(1 for p in [patterns["peak_hours"], patterns["type_timing"],
                                     patterns["priority_adjustment"], patterns["grouping"]] if p)

    return {
        "message": f"{pattern_count} patterns detected",
        "patterns": patterns,
        "patterns_ready": profile.data_points_collected >= 20
    }


@router.get("/patterns/summary")
async def get_pattern_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get high-level pattern summary for dashboard.

    Returns simplified pattern insights:
    - Top 3 productive hours
    - Most common priority changes
    - Number of task grouping patterns
    - Overall learning progress

    **Use Case**: Dashboard widgets, quick insights
    """
    profile = session.exec(
        select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == current_user.id)
    ).first()

    if not profile or profile.data_points_collected < 20:
        return {
            "message": "Not enough data for patterns",
            "progress": f"{profile.data_points_collected if profile else 0}/20 events",
            "summary": {}
        }

    # Parse peak hours
    peak_hours = json.loads(profile.peak_hours) if profile.peak_hours != "{}" else {}
    top_3_hours = []
    if peak_hours:
        sorted_hours = sorted(peak_hours.items(), key=lambda x: x[1], reverse=True)[:3]
        top_3_hours = [int(hour) for hour, _ in sorted_hours]

    # Parse priority patterns
    priority_patterns = json.loads(profile.priority_adjustment_patterns) if profile.priority_adjustment_patterns != "{}" else {}
    common_changes = []
    if priority_patterns:
        for from_pri, to_pris in priority_patterns.items():
            for to_pri, count in to_pris.items():
                common_changes.append(f"{from_pri}→{to_pri} ({count}x)")

    # Parse grouping patterns
    grouping_patterns = json.loads(profile.grouping_patterns) if profile.grouping_patterns != "{}" else {}
    grouping_count = len(grouping_patterns)

    return {
        "message": "Pattern summary",
        "summary": {
            "top_productive_hours": top_3_hours,
            "common_priority_changes": common_changes[:3],
            "task_grouping_patterns": grouping_count,
            "data_points": profile.data_points_collected,
            "last_updated": profile.last_learning_date
        }
    }
