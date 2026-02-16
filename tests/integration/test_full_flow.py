"""Integration test: Full create -> list -> update -> complete -> delete flow."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, list_tasks, update_task, delete_task, mark_complete
from task import Task


def test_full_crud_flow():
    """Test the complete CRUD workflow."""
    storage = TaskStorage()

    # 1. Create tasks
    task1 = create_task(storage, "Buy groceries", "Milk, eggs, bread")
    task2 = create_task(storage, "Pay bills", "Electricity bill due")

    assert task1 is not None
    assert task2 is not None
    assert task1.id != task2.id

    # 2. List tasks
    tasks = list_tasks(storage)
    assert len(tasks) == 2

    # 3. Update a task
    updated = update_task(storage, task1.id, title="Buy groceries and supplies")
    assert updated is not None
    assert updated.title == "Buy groceries and supplies"

    # 4. Mark task as complete
    completed = mark_complete(storage, task1.id, complete=True)
    assert completed is not None
    assert completed.completed is True

    # 5. Verify list shows completion status
    tasks = list_tasks(storage)
    for t in tasks:
        if t.id == task1.id:
            assert t.completed is True

    # 6. Delete a task
    result = delete_task(storage, task2.id)
    assert result is True

    # 7. Verify deletion
    tasks = list_tasks(storage)
    assert len(tasks) == 1

    # 8. Verify remaining task
    remaining = storage.get(task1.id)
    assert remaining is not None
    assert remaining.title == "Buy groceries and supplies"

    print("Full CRUD flow test: PASSED")


def test_multiple_operations_deterministic():
    """Test that operations produce deterministic results."""
    storage = TaskStorage()

    # Create tasks in specific order
    task = create_task(storage, "Test Task", "Description")

    # Get task multiple times
    for _ in range(5):
        retrieved = storage.get(task.id)
        assert retrieved.title == "Test Task"
        assert retrieved.description == "Description"
        assert retrieved.completed is False

    print("Deterministic operations test: PASSED")


if __name__ == "__main__":
    test_full_crud_flow()
    test_multiple_operations_deterministic()
    print("\nAll integration tests passed!")
