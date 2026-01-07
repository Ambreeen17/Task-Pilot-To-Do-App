"""Task data class representing a single todo item."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a single todo item.

    Attributes:
        id: Unique identifier for the task
        title: Short description of the task (required)
        description: Detailed information about the task (optional, defaults to "")
        completed: Whether the task has been completed (defaults to False)
    """

    id: str
    title: str
    description: str = ""
    completed: bool = False

    def to_dict(self) -> dict:
        """
        Convert task to dictionary representation.

        Returns:
            dict with keys: id, title, description, completed
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Create Task from dictionary representation.

        Args:
            data: Dictionary with task data

        Returns:
            Task instance

        Raises:
            KeyError: If required fields (id, title) are missing
        """
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False)
        )

    def __repr__(self) -> str:
        """Return a string representation of the task."""
        return f"Task(id={self.id!r}, title={self.title!r}, completed={self.completed})"
