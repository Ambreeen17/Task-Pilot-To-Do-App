"""Input validation module for the Todo System."""

from typing import Tuple


# Constants
MAX_TITLE_LENGTH = 500
MAX_DESCRIPTION_LENGTH = 5000


def validate_title(title: str) -> Tuple[bool, str]:
    """
    Validate a task title.

    Args:
        title: The title to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if title is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    # Check for empty or whitespace-only
    if not title or not title.strip():
        return False, "Title cannot be empty"

    # Check maximum length
    if len(title) > MAX_TITLE_LENGTH:
        return False, f"Title exceeds maximum length ({MAX_TITLE_LENGTH})"

    return True, ""


def validate_description(description: str) -> Tuple[bool, str]:
    """
    Validate a task description.

    Args:
        description: The description to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if description is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    # Empty description is valid (optional field)
    if not description:
        return True, ""

    # Check maximum length
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description exceeds maximum length ({MAX_DESCRIPTION_LENGTH})"

    return True, ""


def validate_task_id(task_id: str) -> Tuple[bool, str]:
    """
    Validate a task ID format.

    Args:
        task_id: The task ID to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if ID format is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    # Check for empty
    if not task_id:
        return False, "Invalid task ID: empty"

    # Check format: must be a positive integer string
    if not task_id.isdigit():
        return False, f"Invalid task ID format: {task_id}"

    # Check for positive
    if int(task_id) <= 0:
        return False, f"Invalid task ID: {task_id}"

    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing leading/trailing whitespace.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized text with leading/trailing whitespace removed
    """
    return text.strip()
