"""CRUD operations for the Todo System."""

from typing import List, Optional, Tuple, Union

from storage import TaskStorage
from task import Task
from validator import validate_title, validate_description


def create_task(
    storage: TaskStorage,
    title: str,
    description: str = ""
) -> Union[Task, Tuple[bool, str]]:
    """
    Create a new task with a unique ID.

    Args:
        storage: The task storage instance
        title: Task title (required)
        description: Task description (optional, defaults to "")

    Returns:
        Task instance if successful, or (False, error_message) tuple if validation fails
    """
    # Validate title
    is_valid, error = validate_title(title)
    if not is_valid:
        return (False, error)

    # Validate description
    is_valid, error = validate_description(description)
    if not is_valid:
        return (False, error)

    # Generate unique ID and create task
    task_id = storage.generate_id()
    task = Task(
        id=task_id,
        title=title,
        description=description,
        completed=False
    )

    # Store the task
    storage.add(task)

    return task


def list_tasks(storage: TaskStorage) -> List[Task]:
    """
    Retrieve all tasks from storage.

    Args:
        storage: The task storage instance

    Returns:
        List of all Task objects
    """
    return storage.get_all()


def update_task(
    storage: TaskStorage,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Union[Task, Tuple[bool, str]]:
    """
    Update an existing task's title and/or description.

    Args:
        storage: The task storage instance
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated Task instance if successful, or (False, error_message) tuple if validation fails
    """
    # Check if task exists
    existing = storage.get(task_id)
    if existing is None:
        return (False, f"Task not found: {task_id}")

    # Validate title if provided
    if title is not None:
        is_valid, error = validate_title(title)
        if not is_valid:
            return (False, error)

    # Validate description if provided
    if description is not None:
        is_valid, error = validate_description(description)
        if not is_valid:
            return (False, error)

    # Create updated task (preserve existing values for unspecified fields)
    updated = Task(
        id=task_id,
        title=title if title is not None else existing.title,
        description=description if description is not None else existing.description,
        completed=existing.completed
    )

    # Update in storage
    storage.update(task_id, updated)

    return updated


def delete_task(storage: TaskStorage, task_id: str) -> Union[bool, Tuple[bool, str]]:
    """
    Delete a task by ID.

    Args:
        storage: The task storage instance
        task_id: ID of the task to delete

    Returns:
        True if task was deleted, or (False, error_message) tuple if not found
    """
    # Check if task exists
    if not storage.exists(task_id):
        return (False, f"Task not found: {task_id}")

    # Delete the task
    storage.delete(task_id)

    return True


def mark_complete(
    storage: TaskStorage,
    task_id: str,
    complete: bool = True
) -> Union[Task, Tuple[bool, str]]:
    """
    Mark a task as complete or incomplete.

    Args:
        storage: The task storage instance
        task_id: ID of the task to update
        complete: True to mark complete, False to mark incomplete

    Returns:
        Updated Task instance if successful, or (False, error_message) tuple if not found
    """
    # Check if task exists
    existing = storage.get(task_id)
    if existing is None:
        return (False, f"Task not found: {task_id}")

    # Create updated task with new completion status
    updated = Task(
        id=task_id,
        title=existing.title,
        description=existing.description,
        completed=complete
    )

    # Update in storage
    storage.update(task_id, updated)

    return updated
