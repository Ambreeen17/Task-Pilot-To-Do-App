"""Unit tests for operations module."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from operations import create_task, list_tasks, update_task, delete_task, mark_complete
from storage import TaskStorage
from task import Task


class TestCreateTask(unittest.TestCase):
    """Test create_task operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_create_task_creates_with_id(self):
        """Test that create_task creates a task with an ID."""
        task = create_task(self.storage, "Test Task", "Test Description")
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.completed, False)

    def test_create_task_generates_unique_ids(self):
        """Test that create_task generates unique IDs."""
        task1 = create_task(self.storage, "Task 1")
        task2 = create_task(self.storage, "Task 2")
        task3 = create_task(self.storage, "Task 3")

        self.assertNotEqual(task1.id, task2.id)
        self.assertNotEqual(task2.id, task3.id)
        self.assertNotEqual(task1.id, task3.id)

    def test_create_task_stores_task(self):
        """Test that create_task stores the task."""
        task = create_task(self.storage, "Test Task")
        retrieved = self.storage.get(task.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test Task")

    def test_create_task_empty_title_fails(self):
        """Test that create_task with empty title returns error tuple."""
        result = create_task(self.storage, "", "Description")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])

    def test_create_task_default_description_empty(self):
        """Test that create_task uses empty string for default description."""
        task = create_task(self.storage, "Test Task")
        self.assertEqual(task.description, "")


class TestListTasks(unittest.TestCase):
    """Test list_tasks operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_list_empty_returns_empty_list(self):
        """Test that list_tasks on empty storage returns empty list."""
        tasks = list_tasks(self.storage)
        self.assertEqual(tasks, [])

    def test_list_returns_all_tasks(self):
        """Test that list_tasks returns all created tasks."""
        create_task(self.storage, "Task 1")
        create_task(self.storage, "Task 2")
        create_task(self.storage, "Task 3")

        tasks = list_tasks(self.storage)
        self.assertEqual(len(tasks), 3)

    def test_list_returns_task_objects(self):
        """Test that list_tasks returns Task objects."""
        create_task(self.storage, "Test Task")
        tasks = list_tasks(self.storage)
        self.assertIsInstance(tasks[0], Task)


class TestUpdateTask(unittest.TestCase):
    """Test update_task operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_update_title(self):
        """Test updating task title."""
        task = create_task(self.storage, "Original Title")
        updated = update_task(self.storage, task.id, title="New Title")

        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, "New Title")

    def test_update_description(self):
        """Test updating task description."""
        task = create_task(self.storage, "Test Task", "Original Desc")
        updated = update_task(self.storage, task.id, description="New Description")

        self.assertIsNotNone(updated)
        self.assertEqual(updated.description, "New Description")

    def test_update_preserves_other_fields(self):
        """Test that update preserves fields not being updated."""
        task = create_task(self.storage, "Title", "Description")
        # Task is created with completed=False by default
        self.assertEqual(task.completed, False)
        updated = update_task(self.storage, task.id, title="New Title")

        self.assertEqual(updated.description, "Description")
        self.assertEqual(updated.completed, False)

    def test_update_nonexistent_returns_error(self):
        """Test that updating non-existent task returns error."""
        result = update_task(self.storage, "999", title="New Title")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])

    def test_update_empty_title_fails(self):
        """Test that updating with empty title returns error."""
        task = create_task(self.storage, "Test Task")
        result = update_task(self.storage, task.id, title="")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])


class TestDeleteTask(unittest.TestCase):
    """Test delete_task operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_delete_removes_task(self):
        """Test that delete_task removes the task."""
        task = create_task(self.storage, "Test Task")
        result = delete_task(self.storage, task.id)

        self.assertTrue(result)
        self.assertIsNone(self.storage.get(task.id))

    def test_delete_nonexistent_returns_error(self):
        """Test that deleting non-existent task returns error."""
        result = delete_task(self.storage, "999")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])

    def test_delete_other_tasks_unchanged(self):
        """Test that deleting a task doesn't affect others."""
        task1 = create_task(self.storage, "Task 1")
        task2 = create_task(self.storage, "Task 2")

        delete_task(self.storage, task1.id)

        # task2 should still exist
        self.assertIsNotNone(self.storage.get(task2.id))
        self.assertEqual(self.storage.get(task2.id).title, "Task 2")


class TestMarkComplete(unittest.TestCase):
    """Test mark_complete operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_mark_complete_sets_completed_true(self):
        """Test that mark_complete sets completed to True."""
        task = create_task(self.storage, "Test Task")
        # Task is created with completed=False by default
        self.assertFalse(task.completed)
        updated = mark_complete(self.storage, task.id, complete=True)

        self.assertIsNotNone(updated)
        self.assertTrue(updated.completed)

    def test_mark_incomplete_sets_completed_false(self):
        """Test that mark_complete with complete=False sets to False."""
        task = create_task(self.storage, "Test Task")
        # First mark it complete
        mark_complete(self.storage, task.id, complete=True)
        # Then mark it incomplete
        updated = mark_complete(self.storage, task.id, complete=False)

        self.assertIsNotNone(updated)
        self.assertFalse(updated.completed)

    def test_mark_complete_nonexistent_returns_error(self):
        """Test that marking non-existent task returns error."""
        result = mark_complete(self.storage, "999", complete=True)
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])


class TestOperationErrorHandling(unittest.TestCase):
    """Test error handling in operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()

    def test_create_empty_title_error_message(self):
        """Test that create_task with empty title provides error message."""
        result = create_task(self.storage, "", "Description")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIn("title", result[1].lower())

    def test_update_nonexistent_error_message(self):
        """Test that update_task for non-existent task provides error message."""
        result = update_task(self.storage, "999", title="New")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIn("not found", result[1].lower())

    def test_delete_nonexistent_error_message(self):
        """Test that delete_task for non-existent task provides error message."""
        result = delete_task(self.storage, "999")
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIn("not found", result[1].lower())

    def test_mark_complete_nonexistent_error_message(self):
        """Test that mark_complete for non-existent task provides error message."""
        result = mark_complete(self.storage, "999", complete=True)
        self.assertIsInstance(result, tuple)
        self.assertFalse(result[0])
        self.assertIn("not found", result[1].lower())


if __name__ == '__main__':
    unittest.main()
