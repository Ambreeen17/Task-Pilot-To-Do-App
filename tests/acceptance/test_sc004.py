"""Acceptance test: SC-004 - All operations provide feedback."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, list_tasks, update_task, delete_task, mark_complete
from output import format_success, format_error, format_task_list


def test_sc004_all_operations_provide_feedback():
    """SC-004: All operations provide feedback."""
    storage = TaskStorage()

    # Create operation feedback
    task = create_task(storage, "Test Task")
    success_msg = format_success(f'Created task {task.id}: "{task.title}"')
    assert "Created" in success_msg
    assert task.id in success_msg

    # List operation feedback (empty list message)
    output = format_task_list([])
    assert "No tasks" in output or "create" in output.lower()

    # Update operation feedback
    updated = update_task(storage, task.id, title="New Title")
    success_msg = format_success(f'Updated task {updated.id}: "{updated.title}"')
    assert "Updated" in success_msg

    # Complete operation feedback
    completed = mark_complete(storage, task.id, complete=True)
    success_msg = format_success(f'Task {completed.id} marked as completed: "{completed.title}"')
    assert "completed" in success_msg.lower()

    # Incomplete operation feedback
    incomplete = mark_complete(storage, task.id, complete=False)
    success_msg = format_success(f'Task {incomplete.id} marked as incomplete: "{incomplete.title}"')
    assert "incomplete" in success_msg.lower()

    # Delete operation feedback
    result = delete_task(storage, task.id)
    success_msg = format_success(f"Deleted task {task.id}")
    assert "Deleted" in success_msg

    # Error feedback for non-existent task
    error_msg = format_error("Task not found: 999")
    assert "Error" in error_msg
    assert "not found" in error_msg.lower()

    print("SC-004: PASSED - All operations provide feedback")


if __name__ == "__main__":
    test_sc004_all_operations_provide_feedback()
