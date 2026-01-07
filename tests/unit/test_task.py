"""Unit tests for Task data class."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from task import Task


class TestTaskCreation(unittest.TestCase):
    """Test Task creation with all attributes."""

    def test_task_creation_with_all_attributes(self):
        """Test that a task can be created with id, title, description, and completed."""
        task = Task(id="1", title="Test Task", description="Test Description", completed=False)
        self.assertEqual(task.id, "1")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.completed, False)

    def test_task_creation_with_required_attributes_only(self):
        """Test that a task can be created with only required attributes."""
        task = Task(id="2", title="Minimal Task")
        self.assertEqual(task.id, "2")
        self.assertEqual(task.title, "Minimal Task")
        self.assertEqual(task.description, "")
        self.assertEqual(task.completed, False)

    def test_task_creation_defaults(self):
        """Test that default values are applied correctly."""
        task = Task(id="3", title="Default Test")
        self.assertEqual(task.description, "")
        self.assertEqual(task.completed, False)


class TestTaskSerialization(unittest.TestCase):
    """Test Task.to_dict() serialization."""

    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        task = Task(id="1", title="Test", description="Desc", completed=False)
        result = task.to_dict()
        self.assertIsInstance(result, dict)

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict contains all required fields."""
        task = Task(id="1", title="Test Task", description="Test Description", completed=True)
        result = task.to_dict()
        self.assertIn("id", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("completed", result)

    def test_to_dict_values_match(self):
        """Test that to_dict values match the task attributes."""
        task = Task(id="42", title="My Task", description="My Description", completed=True)
        result = task.to_dict()
        self.assertEqual(result["id"], "42")
        self.assertEqual(result["title"], "My Task")
        self.assertEqual(result["description"], "My Description")
        self.assertEqual(result["completed"], True)


class TestTaskDeserialization(unittest.TestCase):
    """Test Task.from_dict() deserialization."""

    def test_from_dict_creates_task(self):
        """Test that from_dict creates a Task from a dictionary."""
        data = {
            "id": "1",
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        }
        task = Task.from_dict(data)
        self.assertIsInstance(task, Task)
        self.assertEqual(task.id, "1")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.completed, False)

    def test_from_dict_with_defaults(self):
        """Test that from_dict uses defaults for missing optional fields."""
        data = {
            "id": "2",
            "title": "Minimal Task"
        }
        task = Task.from_dict(data)
        self.assertEqual(task.description, "")
        self.assertEqual(task.completed, False)

    def test_from_dict_partial_values(self):
        """Test that from_dict handles partial optional fields."""
        data = {
            "id": "3",
            "title": "Partial Task",
            "completed": True
        }
        task = Task.from_dict(data)
        self.assertEqual(task.description, "")
        self.assertEqual(task.completed, True)

    def test_from_dict_roundtrip(self):
        """Test that to_dict and from_dict are inverse operations."""
        original = Task(id="5", title="Roundtrip Task", description="Test", completed=True)
        data = original.to_dict()
        restored = Task.from_dict(data)
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.description, restored.description)
        self.assertEqual(original.completed, restored.completed)


class TestTaskRepr(unittest.TestCase):
    """Test Task __repr__ method."""

    def test_repr_returns_string(self):
        """Test that __repr__ returns a string representation."""
        task = Task(id="1", title="Test Task")
        repr_str = repr(task)
        self.assertIsInstance(repr_str, str)
        self.assertIn("Task", repr_str)
        self.assertIn("1", repr_str)


if __name__ == '__main__':
    unittest.main()
