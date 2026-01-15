"""
Phase 3: AI-Assisted Todo - AI Router

API endpoints for AI-powered features:
- Natural language task parsing
- AI conversations
- Task summaries
- AI insights
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select, desc
import logging
from datetime import datetime
import uuid

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
    features_enabled = os.getenv("AI_FEATURES_ENABLED", "false").lower() == "true"

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
    text: str = Body(..., embed=True),
    timezone: str = Body("UTC", embed=True),
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
        if not text:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text input is required",
            )

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
    intent_id: int = Body(..., embed=True),
    edited_title: str = Body(..., embed=True),
    edited_priority: Optional[str] = Body(None, embed=True),
    edited_due_date: Optional[str] = Body(None, embed=True),
    edited_due_time: Optional[str] = Body(None, embed=True),
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
    intent_id: int = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
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


# US3: Conversational Task Interface

@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def start_conversation(
    topic: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Start a new AI conversation session.

    Args:
        topic: Optional initial topic
        current_user: Authenticated user
        db: Database session

    Returns:
        Created conversation details
    """
    from ..models import AIConversation
    from ..ai.context_manager import get_context_manager

    # Deactivate any existing active conversations
    active_convs = db.exec(
        select(AIConversation)
        .where(AIConversation.user_id == current_user.id)
        .where(AIConversation.status == "active")
    ).all()

    for conv in active_convs:
        conv.status = "closed"
        db.add(conv)

    # Create new conversation
    conversation = AIConversation(
        user_id=current_user.id,
        topic=topic,
        status="active",
        context_window=10
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Initialize context
    cm = get_context_manager()
    ctx = cm.get_context(current_user.id, db)
    ctx.conversation_id = conversation.id
    if topic:
        ctx.last_topic = topic

    return conversation


@router.get("/conversations")
def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    List user's conversation history.

    Args:
        limit: Max records to return
        offset: Pagination offset
        current_user: Authenticated user
        db: Database session

    Returns:
        List of conversations
    """
    from ..models import AIConversation

    conversations = db.exec(
        select(AIConversation)
        .where(AIConversation.user_id == current_user.id)
        .order_by(desc(AIConversation.start_time))
        .offset(offset)
        .limit(limit)
    ).all()

    return conversations


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Get details of a specific conversation.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Conversation with messages
    """
    from ..models import AIConversation, AIMessage

    conversation = db.exec(
        select(AIConversation)
        .where(AIConversation.id == conversation_id)
        .where(AIConversation.user_id == current_user.id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Send a message to the AI assistant.

    Args:
        conversation_id: Conversation ID
        content: User message content
        current_user: Authenticated user
        db: Database session

    Returns:
        AI response message
    """
    from ..models import AIConversation, AIMessage
    from ..ai.client import get_client
    from ..ai.context_manager import get_context_manager
    from ..ai.rate_limiter import get_rate_limiter

    # Check rate limit
    limiter = get_rate_limiter()
    allowed, retry_after = limiter.check_limit(current_user.id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after:.0f} seconds."
        )

    # Get conversation
    conversation = db.exec(
        select(AIConversation)
        .where(AIConversation.id == conversation_id)
        .where(AIConversation.user_id == current_user.id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation is closed"
        )

    # Save user message
    user_msg = AIMessage(
        conversation_id=conversation_id,
        role="user",
        content=content
    )
    db.add(user_msg)
    db.commit()

    # Update context
    cm = get_context_manager()
    cm.update_context(current_user.id, "user", content, db)

    # Get AI response
    try:
        client = get_client()
        # In a real implementation, we would construct a prompt with context/history
        # For now, we'll just send the user message directly
        response_text, token_count = client.call(prompt=content)

        # Consume rate limit token
        limiter.consume(current_user.id)

        # Save AI response
        ai_msg = AIMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            token_count=token_count
        )
        db.add(ai_msg)

        # Update conversation activity
        conversation.last_activity_time = datetime.now()
        db.add(conversation)
        db.commit()
        db.refresh(ai_msg)

        # Update context
        cm.update_context(current_user.id, "assistant", response_text, db)

        return ai_msg

    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service error"
        )


@router.delete("/conversations/{conversation_id}")
def close_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Close an active conversation.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Closing confirmation
    """
    from ..models import AIConversation
    from ..ai.context_manager import get_context_manager

    conversation = db.exec(
        select(AIConversation)
        .where(AIConversation.id == conversation_id)
        .where(AIConversation.user_id == current_user.id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    conversation.status = "closed"
    db.add(conversation)
    db.commit()

    # Persist and clear active context
    cm = get_context_manager()
    cm.close_context(current_user.id, db)

    return {"message": "Conversation closed"}


# US4: AI Task Summaries

@router.post("/summaries", status_code=status.HTTP_201_CREATED)
def generate_summary(
    period_type: str = Body(..., embed=True),
    start_date: str = Body(..., embed=True),
    end_date: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Generate a task summary for a specific period.

    Args:
        period_type: 'daily', 'weekly', 'monthly', or 'custom'
        start_date: Period start date (YYYY-MM-DD)
        end_date: Period end date (YYYY-MM-DD)
        current_user: Authenticated user
        db: Database session

    Returns:
        Generated summary
    """
    from ..models import TaskSummary, Task
    from ..ai.client import get_client
    from ..ai.rate_limiter import get_rate_limiter

    from datetime import date
    import os

    # Check rate limit
    limiter = get_rate_limiter()
    allowed, retry_after = limiter.check_limit(current_user.id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    # Parse dates
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Fetch tasks for period
    # Note: This is a simplification. In reality we'd filter by date range
    tasks = db.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
    ).all()

    # Calculate basic metrics
    total_tasks = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    pending = total_tasks - completed
    # Simplification: assume all uncompleted are pending, no overdue check yet
    overdue = 0
    completion_rate = int((completed / total_tasks * 100) if total_tasks > 0 else 0)

    metrics = {
        "total_tasks": total_tasks,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": completion_rate
    }

    # Generate summary with AI
    try:
        client = get_client()

        # Load prompt template
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ai", "prompts", "summarize_tasks.txt"
        )

        # Fallback if file doesn't exist (robustness)
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(
                tasks_json="[List of tasks would go here]",
                period_type=period_type,
                start_date=start_date,
                end_date=end_date,
                **metrics
            )
        else:
            prompt = f"Summarize these metrics for {period_type}: {metrics}"

        summary_text, _ = client.call(prompt=prompt)
        limiter.consume(current_user.id)

        # Save summary
        summary = TaskSummary(
            user_id=current_user.id,
            period_type=period_type,
            start_date=start,
            end_date=end,
            metrics=metrics,
            summary_text=summary_text
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service failed"
        )


@router.get("/summaries")
def list_summaries(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    List user's generated task summaries.
    """
    from ..models import TaskSummary

    summaries = db.exec(
        select(TaskSummary)
        .where(TaskSummary.user_id == current_user.id)
        .order_by(desc(TaskSummary.generated_at))
        .offset(offset)
        .limit(limit)
    ).all()

    return summaries


# US5: AI Insights

@router.post("/insights/generate")
def generate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Trigger generation of new AI insights.

    Returns:
        List of generated insights
    """
    from ..models import AIInsight, Task
    from ..ai.client import get_client
    from ..ai.rate_limiter import get_rate_limiter
    import json
    import os

    # Check rate limit
    limiter = get_rate_limiter()
    allowed, retry_after = limiter.check_limit(current_user.id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    # Get recent task history (last 30 days)
    # Simplified for now
    tasks = db.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
    ).all()

    if not tasks:
        return {"message": "No tasks to analyze", "insights": []}

    try:
        client = get_client()

        # Load prompt
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ai", "prompts", "generate_insight.txt"
        )

        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(
                tasks_json="[Task data placeholder]",
                days=30,
                insight_type="productivity_trend", # Forcing one type for MVP
                supporting_data_json="{}"
            )

            response_json, _ = client.call_with_json(prompt=prompt)
            limiter.consume(current_user.id)

            # create insight
            insight = AIInsight(
                user_id=current_user.id,
                insight_type="productivity_trend",
                title=response_json.get("title", "New Insight"),
                description=response_json.get("description", "Analysis of your recent activity"),
                supporting_data={},
                priority="Medium"
            )

            db.add(insight)
            db.commit()
            db.refresh(insight)

            return {"message": "Insights generated", "insights": [insight]}

        return {"message": "Insight generation pending", "insights": []}

    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        # Graceful degradation - return empty list instead of error
        return {"message": "Could not generate insights at this time", "insights": []}


@router.get("/insights")
def list_insights(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    List user's AI insights.
    """
    from ..models import AIInsight

    query = select(AIInsight).where(AIInsight.user_id == current_user.id)

    if active_only:
        query = query.where(AIInsight.dismissed_at == None)

    query = query.order_by(desc(AIInsight.created_at))

    insights = db.exec(query).all()
    return insights


@router.post("/insights/{insight_id}/dismiss")
def dismiss_insight(
    insight_id: int,
    reason: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Dismiss an insight.
    """
    from ..models import AIInsight

    insight = db.exec(
        select(AIInsight)
        .where(AIInsight.id == insight_id)
        .where(AIInsight.user_id == current_user.id)
    ).first()

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    insight.dismissed_at = datetime.now()
    insight.dismissed_reason = reason
    db.add(insight)
    db.commit()

    return {"message": "Insight dismissed"}