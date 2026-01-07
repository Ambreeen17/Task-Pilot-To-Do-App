"""Acceptance test: SC-001 - Users can create and verify tasks."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, list_tasks
from output import format_task_list


def test_sc001_create_task_and_verify():
    """SC-001: Users can create and verify tasks."""
    storage = TaskStorage()

    # Create a task
    task = create_task(storage, "Buy groceries", "Milk, eggs, bread")

    # Verify task was created with correct attributes
    assert task is not None
    assert task.id is not None
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False

    # Verify task appears in list
    tasks = list_tasks(storage)
    assert len(tasks) == 1
    assert tasks[0].id == task.id
    assert tasks[0].title == "Buy groceries"

    # Verify formatted output contains task info
    output = format_task_list(tasks)
    assert "Buy groceries" in output
    assert "Milk, eggs, bread" in output

    print("SC-001: PASSED - Users can create and verify tasks")


if __name__ == "__main__":
    test_sc001_create_task_and_verify()
