"""Integration test: Deterministic output verification."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, list_tasks, update_task
from output import format_task_list


def test_id_sequence_determinism():
    """Test that ID generation follows deterministic sequence."""
    storage1 = TaskStorage()
    storage2 = TaskStorage()

    # Create tasks in both storages
    for i in range(10):
        task1 = create_task(storage1, f"Task {i}")
        task2 = create_task(storage2, f"Task {i}")

        # IDs should be the same
        assert task1.id == task2.id, f"ID mismatch at iteration {i}: {task1.id} vs {task2.id}"

    print("ID sequence determinism test: PASSED")


def test_output_format_determinism():
    """Test that output format is consistent."""
    storage = TaskStorage()

    create_task(storage, "Task 1", "Description 1")
    create_task(storage, "Task 2", "Description 2")

    # Get output multiple times
    output1 = format_task_list(list_tasks(storage))
    output2 = format_task_list(list_tasks(storage))

    assert output1 == output2, "Output format is not deterministic"

    print("Output format determinism test: PASSED")


def test_task_state_persistence():
    """Test that task state is consistent."""
    storage = TaskStorage()

    task = create_task(storage, "Test Task", "Description")

    # Modify task through different methods
    update_task(storage, task.id, title="Updated Title")
    update_task(storage, task.id, description="New Description")

    # Verify state is consistent
    retrieved = storage.get(task.id)
    assert retrieved.title == "Updated Title"
    assert retrieved.description == "New Description"

    # Multiple retrievals should yield same result
    for _ in range(10):
        check = storage.get(task.id)
        assert check.title == "Updated Title"
        assert check.description == "New Description"

    print("Task state persistence test: PASSED")


def test_empty_list_always_same():
    """Test that empty list format is always the same."""
    storage = TaskStorage()

    output1 = format_task_list(list_tasks(storage))
    output2 = format_task_list(list_tasks(storage))

    assert output1 == output2
    assert "No tasks" in output1

    print("Empty list determinism test: PASSED")


if __name__ == "__main__":
    test_id_sequence_determinism()
    test_output_format_determinism()
    test_task_state_persistence()
    test_empty_list_always_same()
    print("\nAll determinism tests passed!")
