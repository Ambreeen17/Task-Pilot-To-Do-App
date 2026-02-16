"""Acceptance test: SC-003 - Users can delete and verify removal."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, delete_task, list_tasks


def test_sc003_delete_task_and_verify():
    """SC-003: Users can delete and verify removal."""
    storage = TaskStorage()

    # Create multiple tasks
    task1 = create_task(storage, "Task 1")
    task2 = create_task(storage, "Task 2")
    task3 = create_task(storage, "Task 3")

    # Verify all tasks exist
    tasks = list_tasks(storage)
    assert len(tasks) == 3

    # Delete task 2
    result = delete_task(storage, task2.id)
    assert result is True

    # Verify task 2 is removed
    assert storage.get(task2.id) is None

    # Verify other tasks remain
    tasks = list_tasks(storage)
    assert len(tasks) == 2

    task_ids = [t.id for t in tasks]
    assert task1.id in task_ids
    assert task3.id in task_ids
    assert task2.id not in task_ids

    # Delete task 1
    delete_task(storage, task1.id)

    # Verify only task 3 remains
    tasks = list_tasks(storage)
    assert len(tasks) == 1
    assert tasks[0].id == task3.id

    print("SC-003: PASSED - Users can delete and verify removal")


if __name__ == "__main__":
    test_sc003_delete_task_and_verify()
