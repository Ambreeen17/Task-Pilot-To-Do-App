"""Acceptance test: SC-006 - Edge cases handled gracefully."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, update_task, delete_task, mark_complete
from output import format_error


def test_sc006_edge_cases_handled_gracefully():
    """SC-006: Edge cases handled gracefully without crashes."""
    storage = TaskStorage()

    # Create a task
    task = create_task(storage, "Test Task")
    assert task is not None

    # Test: Empty list display (no crash)
    tasks = list(storage.get_all())
    assert isinstance(tasks, list)

    # Test: Invalid ID operations (return errors, no crash)
    invalid_operations = [
        (update_task, {"task_id": "999", "title": "New"}),
        (delete_task, {"task_id": "999"}),
        (mark_complete, {"task_id": "999", "complete": True}),
    ]

    for op, args in invalid_operations:
        result = op(storage, **args)
        assert isinstance(result, tuple)
        assert result[0] is False
        assert "not found" in result[1].lower()

    # Test: Empty title validation
    result = create_task(storage, "")
    assert isinstance(result, tuple)
    assert result[0] is False
    assert "title" in result[1].lower()

    # Test: Task still exists after failed operations
    remaining = storage.get(task.id)
    assert remaining is not None

    # Test: Delete non-existent task (error, no crash)
    result = delete_task(storage, "999")
    assert isinstance(result, tuple)
    assert result[0] is False

    # Test: Complete non-existent task (error, no crash)
    result = mark_complete(storage, "999", complete=True)
    assert isinstance(result, tuple)
    assert result[0] is False

    # Test: Error message format
    error_msg = format_error("Task not found: 999")
    assert "Error:" in error_msg
    assert "999" in error_msg

    # Verify system is still functional
    new_task = create_task(storage, "New Task After Errors")
    assert new_task is not None

    print("SC-006: PASSED - Edge cases handled gracefully")


if __name__ == "__main__":
    test_sc006_edge_cases_handled_gracefully()
