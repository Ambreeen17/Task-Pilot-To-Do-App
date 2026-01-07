"""Unit tests for CLI module."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from output import format_task, format_task_list, format_success, format_error, format_empty_list
from task import Task


class TestFormatTask(unittest.TestCase):
    """Test task formatting functions."""

    def test_format_task_with_description(self):
        """Test formatting a task with description."""
        task = Task(id="1", title="Buy groceries", description="Milk, eggs, bread", completed=False)
        output = format_task(task)
        self.assertIn("1", output)
        self.assertIn("Buy groceries", output)
        self.assertIn("Milk, eggs, bread", output)
        self.assertIn("Completed: No", output)

    def test_format_task_without_description(self):
        """Test formatting a task without description."""
        task = Task(id="2", title="Call mom", description="", completed=False)
        output = format_task(task)
        self.assertIn("2", output)
        self.assertIn("Call mom", output)
        self.assertIn("Completed: No", output)

    def test_format_task_completed(self):
        """Test formatting a completed task."""
        task = Task(id="3", title="Done task", description="", completed=True)
        output = format_task(task)
        self.assertIn("3", output)
        self.assertIn("Completed: Yes", output)


class TestFormatTaskList(unittest.TestCase):
    """Test task list formatting."""

    def test_format_empty_list(self):
        """Test formatting empty list."""
        output = format_task_list([])
        self.assertIn("tasks", output.lower())
        self.assertIn("create", output.lower())

    def test_format_single_task(self):
        """Test formatting a single task."""
        tasks = [Task(id="1", title="Test Task", description="", completed=False)]
        output = format_task_list(tasks)
        self.assertIn("1", output)
        self.assertIn("Test Task", output)

    def test_format_multiple_tasks(self):
        """Test formatting multiple tasks."""
        tasks = [
            Task(id="1", title="Task 1", description="", completed=False),
            Task(id="2", title="Task 2", description="Desc", completed=True),
            Task(id="3", title="Task 3", description="", completed=False),
        ]
        output = format_task_list(tasks)
        self.assertIn("1", output)
        self.assertIn("2", output)
        self.assertIn("3", output)

    def test_format_includes_summary(self):
        """Test that list formatting includes summary."""
        tasks = [
            Task(id="1", title="Task 1", description="", completed=False),
            Task(id="2", title="Task 2", description="", completed=True),
        ]
        output = format_task_list(tasks)
        self.assertIn("total", output.lower())


class TestFormatSuccess(unittest.TestCase):
    """Test success message formatting."""

    def test_format_success_contains_message(self):
        """Test that success format contains the message."""
        output = format_success("Task created")
        self.assertIn("Task created", output)

    def test_format_success_contains_created(self):
        """Test success message for created task."""
        output = format_success('Created task 1: "Buy groceries"')
        self.assertIn("Created", output)


class TestFormatError(unittest.TestCase):
    """Test error message formatting."""

    def test_format_error_contains_message(self):
        """Test that error format contains the message."""
        output = format_error("Task not found")
        self.assertIn("Task not found", output)
        self.assertIn("Error", output)

    def test_format_error_not_found(self):
        """Test error formatting for not found."""
        output = format_error("Task not found: 5")
        self.assertIn("5", output)


class TestFormatEmptyList(unittest.TestCase):
    """Test empty list message formatting."""

    def test_format_empty_list_message(self):
        """Test that empty list message is user-friendly."""
        output = format_empty_list()
        self.assertIn("No tasks", output)
        self.assertIn("create", output.lower())


if __name__ == '__main__':
    unittest.main()
