"""Acceptance test: SC-002 - Users can update and verify changes."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from operations import create_task, update_task, list_tasks
from output import format_task


def test_sc002_update_task_and_verify():
    """SC-002: Users can update and verify changes."""
    storage = TaskStorage()

    # Create a task
    task = create_task(storage, "Original Title", "Original Description")

    # Update title
    updated = update_task(storage, task.id, title="Updated Title")

    # Verify title was updated
    assert updated is not None
    assert updated.title == "Updated Title"

    # Verify description was preserved
    assert updated.description == "Original Description"

    # Verify in storage
    retrieved = storage.get(task.id)
    assert retrieved.title == "Updated Title"

    # Update description
    updated2 = update_task(storage, task.id, description="New Description")

    # Verify both fields are correct
    assert updated2.title == "Updated Title"
    assert updated2.description == "New Description"

    # Verify in formatted output
    output = format_task(updated2)
    assert "Updated Title" in output
    assert "New Description" in output

    print("SC-002: PASSED - Users can update and verify changes")


if __name__ == "__main__":
    test_sc002_update_task_and_verify()
