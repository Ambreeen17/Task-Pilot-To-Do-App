"""Integration test: Edge cases handling."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, list_tasks, update_task, delete_task, mark_complete
from validator import validate_title, validate_description


def test_empty_list_handling():
    """Test handling of empty task list."""
    storage = TaskStorage()

    tasks = list_tasks(storage)
    assert tasks == []

    # Should be able to create after empty list
    task = create_task(storage, "First Task")
    assert task is not None

    tasks = list_tasks(storage)
    assert len(tasks) == 1

    print("Empty list handling test: PASSED")


def test_invalid_task_id_handling():
    """Test handling of invalid task IDs."""
    storage = TaskStorage()

    # Create a task first
    task = create_task(storage, "Test Task")

    # Try operations with invalid IDs
    invalid_ids = ["", "abc", "-1", "0", "1.5", "999"]

    for task_id in invalid_ids:
        result = storage.get(task_id)
        assert result is None, f"Expected None for invalid ID: {task_id}"

    # Valid ID should still work
    valid = storage.get(task.id)
    assert valid is not None

    print("Invalid ID handling test: PASSED")


def test_duplicate_task_creation():
    """Test that tasks with same title but different IDs are allowed."""
    storage = TaskStorage()

    # Create multiple tasks with same title
    task1 = create_task(storage, "Same Title", "Description 1")
    task2 = create_task(storage, "Same Title", "Description 2")
    task3 = create_task(storage, "Same Title", "Description 3")

    # Each should have unique ID
    assert task1.id != task2.id
    assert task2.id != task3.id
    assert task1.id != task3.id

    print("Duplicate title handling test: PASSED")


def test_special_characters_handling():
    """Test handling of special characters in titles and descriptions."""
    storage = TaskStorage()

    # Test various special characters
    special_title = "Task with \"quotes\", 'apostrophes', and \\ backslash"
    special_desc = "Description with\ttab\nnewline,and   multiple   spaces"

    task = create_task(storage, special_title, special_desc)

    assert task.title == special_title
    assert task.description == special_desc

    # Verify storage preserves characters
    retrieved = storage.get(task.id)
    assert retrieved.title == special_title
    assert retrieved.description == special_desc

    print("Special characters handling test: PASSED")


def test_very_long_content_handling():
    """Test handling of very long title and description."""
    storage = TaskStorage()

    # Max length for title is 500, description is 5000
    long_title = "x" * 500
    long_desc = "y" * 5000

    task = create_task(storage, long_title, long_desc)

    assert task is not None
    assert len(task.title) == 500
    assert len(task.description) == 5000

    # Verify storage preserves length
    retrieved = storage.get(task.id)
    assert len(retrieved.title) == 500
    assert len(retrieved.description) == 5000

    print("Long content handling test: PASSED")


def test_unicode_handling():
    """Test handling of unicode characters."""
    storage = TaskStorage()

    unicode_title = "Tâsk with açcénts and 日本語"
    unicode_desc = "描述 with 中文 and emojis 🎉"

    task = create_task(storage, unicode_title, unicode_desc)

    assert task.title == unicode_title
    assert task.description == unicode_desc

    print("Unicode handling test: PASSED")


def test_update_no_changes():
    """Test update with no actual changes."""
    storage = TaskStorage()

    task = create_task(storage, "Test Task", "Description")

    # Update with same values
    result = update_task(storage, task.id, title="Test Task", description="Description")

    assert result is not None
    assert result.title == "Test Task"
    assert result.description == "Description"

    print("Update no changes test: PASSED")


def test_complete_already_completed():
    """Test marking already completed task as complete."""
    storage = TaskStorage()

    task = create_task(storage, "Test Task")
    mark_complete(storage, task.id, complete=True)

    # Mark complete again
    result = mark_complete(storage, task.id, complete=True)
    assert result is not None
    assert result.completed is True

    print("Complete already completed test: PASSED")


def test_delete_already_deleted():
    """Test deleting already deleted task."""
    storage = TaskStorage()

    task = create_task(storage, "Test Task")
    delete_task(storage, task.id)

    # Try to delete again
    result = delete_task(storage, task.id)
    assert isinstance(result, tuple)
    assert result[0] is False

    print("Delete already deleted test: PASSED")


if __name__ == "__main__":
    test_empty_list_handling()
    test_invalid_task_id_handling()
    test_duplicate_task_creation()
    test_special_characters_handling()
    test_very_long_content_handling()
    test_unicode_handling()
    test_update_no_changes()
    test_complete_already_completed()
    test_delete_already_deleted()
    print("\nAll edge case tests passed!")
