"""Output formatting module for the Todo System CLI."""

from typing import List

from task import Task


def format_task(task: Task) -> str:
    """
    Format a single task for display.

    Args:
        task: The Task to format

    Returns:
        Formatted string representation of the task
    """
    status = "[x]" if task.completed else "[ ]"
    lines = [
        f"Task {task.id}:",
        f"  Title: {task.title}",
        f"  Description: {task.description if task.description else '(none)'}",
        f"  Completed: {'Yes' if task.completed else 'No'}"
    ]
    return "\n".join(lines)


def format_task_list(tasks: List[Task]) -> str:
    """
    Format a list of tasks for display.

    Args:
        tasks: List of Task objects

    Returns:
        Formatted string representation of the task list
    """
    if not tasks:
        return format_empty_list()

    lines = ["Tasks:"]
    completed_count = 0

    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        if task.description:
            lines.append(f"{task.id}. {status} {task.title} - {task.description}")
        else:
            lines.append(f"{task.id}. {status} {task.title}")
        if task.completed:
            completed_count += 1

    total = len(tasks)
    pending = total - completed_count
    lines.append(f"\n{total} task(s) total ({completed_count} completed, {pending} pending)")

    return "\n".join(lines)


def format_success(message: str) -> str:
    """
    Format a success message.

    Args:
        message: The success message

    Returns:
        Formatted success message
    """
    return message


def format_error(message: str) -> str:
    """
    Format an error message.

    Args:
        message: The error message

    Returns:
        Formatted error message
    """
    return f"Error: {message}"


def format_empty_list() -> str:
    """
    Format a message for when the task list is empty.

    Returns:
        User-friendly empty list message
    """
    return "No tasks yet. Create one with: python main.py create \"Your task\""
