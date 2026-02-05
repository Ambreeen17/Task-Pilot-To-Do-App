"""
Phase 3: AI-Assisted Todo - AI Router

API endpoints for AI-powered features:
- Natural language task parsing
- AI conversations
- Task summaries
- AI insights
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import logging

from ..database import get_session
from ..dependencies import get_current_user
from ..models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health")
def ai_health_check():
    """
    Check if AI services are configured and available.

    Returns:
        Status of AI services
    """
    import os

    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    features_enabled = os.getenv("AI_FEATURES_ENABLED", "true").lower() == "true"

    return {
        "status": "ok" if (api_key_set and features_enabled) else "degraded",
        "api_key_configured": api_key_set,
        "features_enabled": features_enabled,
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
    }


@router.get("/rate-limit")
def get_rate_limit_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's rate limit status.

    Returns:
        Remaining requests and limit info
    """
    from ..ai.rate_limiter import get_rate_limiter

    limiter = get_rate_limiter()
    remaining = limiter.get_remaining(current_user.id)

    return {
        "user_id": str(current_user.id),
        "requests_remaining": remaining,
        "requests_per_day": limiter.requests_per_day,
        "window_hours": limiter.window_hours,
    }


# US1: Natural Language Task Creation Endpoints


@router.post("/parse")
def parse_natural_language(
    text: str,
    timezone: str = "UTC",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Parse natural language input into structured task intent.

    Args:
        text: Natural language task description
        timezone: User's timezone for date parsing
        current_user: Authenticated user
        db: Database session

    Returns:
        Parsed intent with confidence scores and recommendation
    """
    from ..ai.rate_limiter import get_rate_limiter
    from ..ai.parser import parse_task_with_ai, get_recommendation

    # Check rate limit
    limiter = get_rate_limiter()
    allowed, retry_after = limiter.check_limit(current_user.id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Try again in {retry_after:.0f} seconds.",
                "retry_after": retry_after,
            },
        )

    # Parse with AI (T025: graceful degradation)
    try:
        intent, token_count = parse_task_with_ai(
            user_input=text, user_id=current_user.id, user_timezone=timezone
        )

        # Consume rate limit token
        limiter.consume(current_user.id)

        # Get recommendation
        recommendation = get_recommendation(intent)

        # T026: Check for 3-strike fallback
        # Track parse failures in session (simplified - could use DB or cache)
        overall_confidence = sum(intent.confidence_scores.values()) / len(
            intent.confidence_scores
        )

        if overall_confidence < 0.5:  # Very low confidence
            # Increment failure count (simplified - just return fallback suggestion)
            recommendation = "fallback_to_manual"
            message = "We're having trouble understanding. Please use manual entry form."
        else:
            # Map recommendation to response message
            messages = {
                "auto_accept": "Task ready to create",
                "review": "Please review the extracted details",
                "clarify": "Please clarify your task description",
            }
            message = messages.get(recommendation, "Please review")

        return {
            "intent": {
                "original_text": intent.original_text,
                "extracted_title": intent.extracted_title,
                "extracted_priority": intent.extracted_priority,
                "extracted_due_date": (
                    intent.extracted_due_date.isoformat()
                    if intent.extracted_due_date
                    else None
                ),
                "extracted_due_time": (
                    intent.extracted_due_time.isoformat()
                    if intent.extracted_due_time
                    else None
                ),
                "confidence_scores": intent.confidence_scores,
            },
            "recommendation": recommendation,
            "message": message,
            "fallback_url": "/tasks/create" if recommendation == "fallback_to_manual" else None,
        }

    except Exception as e:
        # T025: Graceful degradation - AI service failures
        logger.error(f"Failed to parse task: {e}")

        return {
            "intent": {
                "original_text": text,
                "extracted_title": None,
                "extracted_priority": None,
                "extracted_due_date": None,
                "extracted_due_time": None,
                "confidence_scores": {"title": 0.0, "priority": 0.0, "due_date": 0.0},
            },
            "recommendation": "fallback_to_manual",
            "message": "AI service is temporarily unavailable. Please use manual entry.",
            "fallback_url": "/tasks/create",
            "error": "ai_service_unavailable",
        }


@router.post("/parse/confirm", status_code=status.HTTP_201_CREATED)
def confirm_parsed_intent(
    intent_id: int,
    edited_title: str,
    edited_priority: Optional[str] = None,
    edited_due_date: Optional[str] = None,
    edited_due_time: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Confirm parsed intent and create task.

    Args:
        intent_id: Parsed intent ID (not yet implemented - will be 0 for now)
        edited_title: Final task title (user-edited or as-parsed)
        edited_priority: Final priority (user-edited or as-parsed)
        edited_due_date: Final due date (user-edited or as-parsed)
        edited_due_time: Final due time (user-edited or as-parsed)
        current_user: Authenticated user
        db: Database session

    Returns:
        Created task details
    """
    from ..models import Task
    from datetime import datetime, time as dt_time

    # Create task in Phase 2 system
    task_data = {
        "user_id": current_user.id,
        "title": edited_title,
        "priority": edited_priority or "Medium",
        "completed": False,
    }

    # Combine due_date and due_time into single datetime
    if edited_due_date:
        due_datetime = datetime.fromisoformat(edited_due_date)
        if edited_due_time:
            due_time = dt_time.fromisoformat(edited_due_time)
            due_datetime = due_datetime.replace(
                hour=due_time.hour, minute=due_time.minute, second=due_time.second
            )
        task_data["due_date"] = due_datetime

    task = Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task": {
            "id": str(task.id),
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": "pending",
            "created_at": task.created_at.isoformat(),
        },
        "intent_id": intent_id,
        "message": "Task created successfully",
    }


@router.post("/parse/reject")
def reject_parsed_intent(
    intent_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Reject parsed intent (user does not create task).

    Args:
        intent_id: Parsed intent ID
        reason: Optional feedback on why rejected
        current_user: Authenticated user

    Returns:
        Rejection confirmation
    """
    # Log rejection for model improvement
    logger.info(
        f"User {current_user.id} rejected intent {intent_id}",
        extra={"reason": reason, "intent_id": intent_id},
    )

    return {
        "message": "Intent rejected",
        "intent_id": intent_id,
    }


# Placeholder routes for Phase 3 implementation
# These will be implemented in subsequent tasks (US1-US6)

# US1: Natural Language Task Creation
# POST /ai/parse - Parse natural language to task intent
# POST /ai/parse/confirm - Confirm parsed intent and create task
# POST /ai/parse/reject - Reject parsed intent

# US3: Conversational Task Interface
# POST /ai/conversations - Start new conversation
# GET /ai/conversations - List user conversations
# GET /ai/conversations/{id} - Get conversation details
# POST /ai/conversations/{id}/messages - Send message to conversation
# DELETE /ai/conversations/{id} - Close conversation

# US4: AI Task Summaries
# POST /ai/summaries - Generate task summary for period
# GET /ai/summaries - List user summaries
# GET /ai/summaries/{id} - Get summary details

# US5: AI Insights & Recommendations
# POST /ai/insights/generate - Generate insights from task history
# GET /ai/insights - List active insights
# GET /ai/insights/{id} - Get insight details
# POST /ai/insights/{id}/dismiss - Dismiss insight
