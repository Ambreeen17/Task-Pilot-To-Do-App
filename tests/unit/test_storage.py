"""Unit tests for TaskStorage class."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage import TaskStorage
from task import Task


class TestTaskStorageAddGet(unittest.TestCase):
    """Test TaskStorage.add() and get() methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()
        self.task = Task(id="1", title="Test Task", description="Test Description", completed=False)

    def test_add_increases_count(self):
        """Test that adding a task increases the task count."""
        initial_count = len(self.storage.get_all())
        self.storage.add(self.task)
        self.assertEqual(len(self.storage.get_all()), initial_count + 1)

    def test_get_returns_task(self):
        """Test that get returns the correct task."""
        self.storage.add(self.task)
        retrieved = self.storage.get("1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "1")
        self.assertEqual(retrieved.title, "Test Task")

    def test_get_nonexistent_returns_none(self):
        """Test that getting a non-existent task returns None."""
        result = self.storage.get("999")
        self.assertIsNone(result)

    def test_get_after_multiple_adds(self):
        """Test that get works correctly after adding multiple tasks."""
        task1 = Task(id="1", title="Task 1")
        task2 = Task(id="2", title="Task 2")
        task3 = Task(id="3", title="Task 3")

        self.storage.add(task1)
        self.storage.add(task2)
        self.storage.add(task3)

        self.assertEqual(self.storage.get("1").title, "Task 1")
        self.assertEqual(self.storage.get("2").title, "Task 2")
        self.assertEqual(self.storage.get("3").title, "Task 3")


class TestIDGeneration(unittest.TestCase):
    """Test ID generation uniqueness."""

    def test_id_generation_format(self):
        """Test that generated IDs are strings."""
        storage = TaskStorage()
        task = Task(id=storage.generate_id(), title="Test")
        self.assertIsInstance(task.id, str)

    def test_multiple_ids_are_unique(self):
        """Test that multiple generated IDs are unique."""
        storage = TaskStorage()
        ids = set()
        for _ in range(100):
            task = Task(id=storage.generate_id(), title="Test")
            self.assertNotIn(task.id, ids)
            ids.add(task.id)

    def test_id_sequence(self):
        """Test that ID generation follows sequential pattern."""
        storage = TaskStorage()
        id1 = storage.generate_id()
        id2 = storage.generate_id()
        id3 = storage.generate_id()

        # IDs should be sequential strings
        self.assertEqual(id1, "1")
        self.assertEqual(id2, "2")
        self.assertEqual(id3, "3")


class TestTaskStorageCRUD(unittest.TestCase):
    """Test TaskStorage CRUD operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = TaskStorage()
        self.task = Task(id="1", title="Original Title", description="Original Desc", completed=False)

    def test_update_modifies_task(self):
        """Test that update modifies an existing task."""
        self.storage.add(self.task)
        updated_task = Task(id="1", title="Updated Title", description="Updated Desc", completed=True)
        result = self.storage.update("1", updated_task)

        self.assertTrue(result)
        self.assertEqual(self.storage.get("1").title, "Updated Title")
        self.assertEqual(self.storage.get("1").completed, True)

    def test_update_nonexistent_returns_false(self):
        """Test that updating a non-existent task returns False."""
        task = Task(id="999", title="Test")
        result = self.storage.update("999", task)
        self.assertFalse(result)

    def test_delete_removes_task(self):
        """Test that delete removes a task from storage."""
        self.storage.add(self.task)
        result = self.storage.delete("1")
        self.assertTrue(result)
        self.assertIsNone(self.storage.get("1"))

    def test_delete_nonexistent_returns_false(self):
        """Test that deleting a non-existent task returns False."""
        result = self.storage.delete("999")
        self.assertFalse(result)

    def test_exists_returns_true_for_added_task(self):
        """Test that exists returns True for an added task."""
        self.storage.add(self.task)
        self.assertTrue(self.storage.exists("1"))

    def test_exists_returns_false_for_nonexistent(self):
        """Test that exists returns False for non-existent task."""
        self.assertFalse(self.storage.exists("999"))

    def test_get_all_returns_all_tasks(self):
        """Test that get_all returns all added tasks."""
        task1 = Task(id="1", title="Task 1")
        task2 = Task(id="2", title="Task 2")
        task3 = Task(id="3", title="Task 3")

        self.storage.add(task1)
        self.storage.add(task2)
        self.storage.add(task3)

        all_tasks = self.storage.get_all()
        self.assertEqual(len(all_tasks), 3)

    def test_get_all_empty_returns_empty_list(self):
        """Test that get_all on empty storage returns empty list."""
        all_tasks = self.storage.get_all()
        self.assertEqual(len(all_tasks), 0)


class TestStorageStateManagement(unittest.TestCase):
    """Test storage state management."""

    def test_storage_isolation(self):
        """Test that different storage instances are isolated."""
        storage1 = TaskStorage()
        storage2 = TaskStorage()

        task1 = Task(id="1", title="Task in Storage 1")
        task2 = Task(id="1", title="Task in Storage 2")

        storage1.add(task1)
        storage2.add(task2)

        self.assertEqual(storage1.get("1").title, "Task in Storage 1")
        self.assertEqual(storage2.get("1").title, "Task in Storage 2")

    def test_task_modification_after_add(self):
        """Test that modifying a task after add does affect storage (dataclass is mutable)."""
        storage = TaskStorage()
        original = Task(id="1", title="Original")
        storage.add(original)

        # Modify the original task object
        original.title = "Modified"
        original.completed = True

        # Storage reflects the modification since dataclass is mutable
        stored = storage.get("1")
        self.assertEqual(stored.title, "Modified")
        self.assertEqual(stored.completed, True)


if __name__ == '__main__':
    unittest.main()
