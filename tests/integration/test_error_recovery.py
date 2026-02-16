"""Integration test: Error recovery scenarios."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, update_task, delete_task, mark_complete
from validator import validate_title


def test_error_recovery_after_invalid_operation():
    """Test that system recovers after invalid operations."""
    storage = TaskStorage()

    # Create a valid task
    task = create_task(storage, "Valid Task")
    assert task is not None

    # Try invalid operations - system should handle gracefully
    # Empty title
    result = create_task(storage, "", "Description")
    assert isinstance(result, tuple)
    assert result[0] is False

    # Existing task should still be there
    remaining = storage.get(task.id)
    assert remaining is not None

    # Try updating with empty title
    result = update_task(storage, task.id, title="")
    assert isinstance(result, tuple)
    assert result[0] is False

    # Task should be unchanged
    updated = storage.get(task.id)
    assert updated.title == "Valid Task"

    print("Error recovery test: PASSED")


def test_operations_after_not_found_errors():
    """Test operations continue working after 'not found' errors."""
    storage = TaskStorage()

    # Create a task
    task = create_task(storage, "Test Task")

    # Try operations on non-existent task
    result = update_task(storage, "999", title="New")
    assert isinstance(result, tuple)
    assert result[0] is False

    result = delete_task(storage, "999")
    assert isinstance(result, tuple)
    assert result[0] is False

    result = mark_complete(storage, "999", complete=True)
    assert isinstance(result, tuple)
    assert result[0] is False

    # Original task should still work
    updated = update_task(storage, task.id, title="Updated Task")
    assert updated is not None
    assert updated.title == "Updated Task"

    print("Not found error recovery test: PASSED")


def test_system_state_after_validation_failures():
    """Test system state integrity after validation failures."""
    storage = TaskStorage()

    initial_count = storage.count()

    # Multiple failed creates
    for _ in range(5):
        create_task(storage, "", "Empty title")

    # Count should not have changed
    assert storage.count() == initial_count

    # Valid create should work
    task = create_task(storage, "Valid Task")
    assert task is not None
    assert storage.count() == initial_count + 1

    print("Validation failure state test: PASSED")


if __name__ == "__main__":
    test_error_recovery_after_invalid_operation()
    test_operations_after_not_found_errors()
    test_system_state_after_validation_failures()
    print("\nAll error recovery tests passed!")
