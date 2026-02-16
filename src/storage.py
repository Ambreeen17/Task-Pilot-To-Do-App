"""In-memory storage for tasks."""

from typing import Dict, List, Optional


class TaskStorage:
    """
    In-memory storage for tasks.

    Provides O(1) lookup complexity for all operations.
    Data persists only for the current session.
    """

    def __init__(self):
        """Initialize an empty storage with sequential ID counter."""
        self._tasks: Dict[str, "Task"] = {}
        self._next_id: int = 1

    def add(self, task: "Task") -> None:
        """
        Add a task to storage.

        Args:
            task: Task to add
        """
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Optional["Task"]:
        """
        Retrieve a task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> List["Task"]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks (order is not guaranteed)
        """
        return list(self._tasks.values())

    def update(self, task_id: str, task: "Task") -> bool:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            task: New task data

        Returns:
            True if task was updated, False if task not found
        """
        if task_id not in self._tasks:
            return False
        self._tasks[task_id] = task
        return True

    def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task not found
        """
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def exists(self, task_id: str) -> bool:
        """
        Check if a task exists.

        Args:
            task_id: ID to check

        Returns:
            True if task exists, False otherwise
        """
        return task_id in self._tasks

    def generate_id(self) -> str:
        """
        Generate a unique sequential task ID.

        Returns:
            String representation of the next ID (e.g., "1", "2", "3", ...)
        """
        task_id = str(self._next_id)
        self._next_id += 1
        return task_id

    def count(self) -> int:
        """Return the number of tasks in storage."""
        return len(self._tasks)
