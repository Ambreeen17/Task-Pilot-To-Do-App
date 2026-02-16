"""Acceptance test: SC-005 - All tasks have unique identifiers."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task


def test_sc005_all_tasks_have_unique_ids():
    """SC-005: All tasks have unique identifiers."""
    storage = TaskStorage()

    # Create many tasks
    task_ids = set()
    num_tasks = 100

    for i in range(num_tasks):
        task = create_task(storage, f"Task {i}")
        assert task.id is not None
        assert task.id not in task_ids, f"Duplicate ID found: {task.id}"
        task_ids.add(task.id)

    # Verify all IDs are unique
    assert len(task_ids) == num_tasks

    # Verify ID format (sequential)
    sorted_ids = sorted(task_ids, key=lambda x: int(x))
    for i, task_id in enumerate(sorted_ids, start=1):
        assert task_id == str(i), f"Expected ID {i}, got {task_id}"

    # Verify storage count matches
    assert storage.count() == num_tasks

    print("SC-005: PASSED - All tasks have unique identifiers")


if __name__ == "__main__":
    test_sc005_all_tasks_have_unique_ids()
