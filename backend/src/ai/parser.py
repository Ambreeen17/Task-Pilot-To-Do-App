"""
Phase 3: AI-Assisted Todo - Natural Language Parser

Parses natural language input into structured task data using Claude API.
"""

import os
import json
import logging
import uuid
from datetime import datetime, date, time, timedelta
from typing import Optional, Tuple
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
import pytz

from .client import get_client
from ..models import ParsedTaskIntent

logger = logging.getLogger(__name__)


def parse_date(
    date_str: str, user_timezone: str = "UTC", reference_date: Optional[datetime] = None
) -> Optional[date]:
    """
    Parse natural language date with timezone awareness.

    Args:
        date_str: Date string (e.g., "tomorrow", "next Friday", "2026-01-15")
        user_timezone: User's timezone (default: UTC)
        reference_date: Reference date for relative calculations (default: now)

    Returns:
        Parsed date or None if parsing fails

    Examples:
        >>> parse_date("tomorrow", "UTC")
        datetime.date(2026, 1, 11)
        >>> parse_date("next Friday", "America/New_York")
        datetime.date(2026, 1, 17)
    """
    try:
        tz = pytz.timezone(user_timezone)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"Unknown timezone {user_timezone}, using UTC")
        tz = pytz.UTC

    now = reference_date or datetime.now(tz)
    date_str_lower = date_str.lower().strip()

    # Handle common relative dates
    if date_str_lower in ["today", "now"]:
        return now.date()

    if date_str_lower == "tomorrow":
        return (now + timedelta(days=1)).date()

    if date_str_lower == "yesterday":
        return (now - timedelta(days=1)).date()

    # Handle "next week"
    if "next week" in date_str_lower:
        return (now + timedelta(days=7)).date()

    # Handle "in X days"
    if "in" in date_str_lower and "day" in date_str_lower:
        try:
            parts = date_str_lower.split()
            if len(parts) >= 2 and parts[0] == "in":
                days = int(parts[1])
                return (now + timedelta(days=days)).date()
        except (ValueError, IndexError):
            pass

    # Handle "next [day of week]"
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    if "next" in date_str_lower:
        for day_name, day_num in weekdays.items():
            if day_name in date_str_lower:
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:  # Target day already passed this week
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).date()

    # Handle "this [day of week]"
    if "this" in date_str_lower:
        for day_name, day_num in weekdays.items():
            if day_name in date_str_lower:
                days_ahead = day_num - now.weekday()
                if days_ahead < 0:  # Already passed, use next week
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).date()

    # Fall back to dateutil parser
    try:
        parsed = date_parser.parse(date_str, default=now, fuzzy=True)
        return parsed.date()
    except (ValueError, date_parser.ParserError) as e:
        logger.debug(f"Failed to parse date '{date_str}': {e}")
        return None


def parse_time(time_str: str) -> Optional[time]:
    """
    Parse time string to time object.

    Args:
        time_str: Time string (e.g., "5pm", "17:00", "3:30 PM")

    Returns:
        Parsed time or None if parsing fails

    Examples:
        >>> parse_time("5pm")
        datetime.time(17, 0)
        >>> parse_time("3:30 PM")
        datetime.time(15, 30)
    """
    try:
        # Parse using dateutil
        parsed = date_parser.parse(time_str, fuzzy=True)
        return parsed.time()
    except (ValueError, date_parser.ParserError) as e:
        logger.debug(f"Failed to parse time '{time_str}': {e}")
        return None


def parse_task_with_ai(
    user_input: str,
    user_id: uuid.UUID,
    user_timezone: str = "UTC",
) -> Tuple[Optional[ParsedTaskIntent], int]:
    """
    Parse natural language task using Claude API.

    Args:
        user_input: User's natural language input
        user_id: User UUID
        user_timezone: User's timezone for date parsing

    Returns:
        Tuple of (ParsedTaskIntent or None, token_count)

    Raises:
        Exception: If Claude API call fails
    """
    client = get_client()

    # Load prompt template
    prompt_path = os.path.join(
        os.path.dirname(__file__), "prompts", "parse_task.txt"
    )
    with open(prompt_path, "r") as f:
        prompt_template = f.read()

    # Calculate reference dates for template
    now = datetime.now(pytz.timezone(user_timezone))
    tomorrow = now + timedelta(days=1)
    next_friday = now + timedelta(days=(4 - now.weekday() + 7) % 7)
    three_days = now + timedelta(days=3)

    # Fill template
    prompt = prompt_template.format(
        user_input=user_input,
        tomorrow_date=tomorrow.strftime("%Y-%m-%d"),
        next_friday_date=next_friday.strftime("%Y-%m-%d"),
        three_days_from_now=three_days.strftime("%Y-%m-%d"),
        current_date=now.strftime("%Y-%m-%d"),
        user_timezone=user_timezone,
    )

    # Call Claude API
    try:
        response_json, token_count = client.call_with_json(prompt=prompt)

        # Extract fields
        title = response_json.get("title")
        priority = response_json.get("priority")
        due_date_str = response_json.get("due_date")
        due_time_str = response_json.get("due_time")
        confidence = response_json.get("confidence", {})

        # Parse date and time
        extracted_due_date = None
        extracted_due_time = None

        if due_date_str:
            extracted_due_date = parse_date(due_date_str, user_timezone)

        if due_time_str:
            extracted_due_time = parse_time(due_time_str)

        # Create ParsedTaskIntent
        intent = ParsedTaskIntent(
            message_id=0,  # Will be set when associated with message
            original_text=user_input,
            extracted_title=title,
            extracted_priority=priority,
            extracted_due_date=extracted_due_date,
            extracted_due_time=extracted_due_time,
            confidence_scores={
                "title": float(confidence.get("title", 0.0)),
                "priority": float(confidence.get("priority", 0.0)),
                "due_date": float(confidence.get("due_date", 0.0)),
            },
            confirmed=False,
        )

        logger.info(
            f"Parsed task for user {user_id}: title={title}, confidence={confidence}"
        )

        return intent, token_count

    except Exception as e:
        logger.error(f"Failed to parse task with AI: {e}")
        raise


def calculate_overall_confidence(intent: ParsedTaskIntent) -> float:
    """
    Calculate overall confidence score from individual field scores.

    Args:
        intent: ParsedTaskIntent with confidence_scores

    Returns:
        Overall confidence (0.0-1.0), weighted average
    """
    # Weight: title is most important
    weights = {"title": 0.5, "priority": 0.25, "due_date": 0.25}

    total = 0.0
    for field, weight in weights.items():
        total += intent.confidence_scores.get(field, 0.0) * weight

    return total


def get_recommendation(intent: ParsedTaskIntent) -> str:
    """
    Get recommendation based on confidence scores.

    Args:
        intent: ParsedTaskIntent with confidence_scores

    Returns:
        Recommendation: "auto_accept", "review", or "clarify"
    """
    scores = intent.confidence_scores
    title_conf = scores.get("title", 0.0)
    priority_conf = scores.get("priority", 0.0)
    due_date_conf = scores.get("due_date", 0.0)

    # Auto-accept: all fields ≥0.9
    if all(score >= 0.9 for score in [title_conf, priority_conf, due_date_conf]):
        return "auto_accept"

    # Clarify: any field <0.7
    if any(score < 0.7 for score in [title_conf, priority_conf, due_date_conf]):
        return "clarify"

    # Review: everything else
    return "review"
