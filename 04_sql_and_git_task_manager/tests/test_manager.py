"""Unit and Integration tests for TaskManager."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.connection import get_db_connection
from managers.task_manager import TaskManager
from models.exceptions import (
    CategoryNotFoundError,
    TaskNotFoundError,
    ValidationError,
)


class TestTaskManager(unittest.TestCase):
    """Integration test suite verifying TaskManager CRUD and business logic."""

    @classmethod
    def setUpClass(cls):
        """Ensure database schema is initialized before test suite runs."""
        cls.db = get_db_connection()
        cls.db.init_schema()
        cls.manager = TaskManager(cls.db)

    def setUp(self):
        """Clean tables before each test to guarantee isolation."""
        with self.db.get_cursor(dict_cursor=False) as cur:
            cur.execute("TRUNCATE task_tags, tags, tasks, categories RESTART IDENTITY CASCADE;")

    def test_create_and_get_task(self):
        """Test creating a task with a category and tags, then retrieving it."""
        cat = self.manager.create_category("Engineering", "Core development")
        task = self.manager.create_task(
            title="Implement OAuth2",
            description="Add JWT-based auth",
            category_id=cat.id,
            priority="high",
            due_date="2026-10-15",
            tags=["auth", "security"],
        )
        self.assertIsNotNone(task.id)
        self.assertEqual(task.category_name, "Engineering")

        # Retrieve through get_task (tests LEFT JOIN)
        fetched = self.manager.get_task(task.id)
        self.assertEqual(fetched.title, "Implement OAuth2")
        self.assertEqual(fetched.category_name, "Engineering")
        self.assertEqual(sorted(fetched.tags), ["auth", "security"])

    def test_list_tasks_with_filters(self):
        """Test listing tasks with dynamic status and priority filters."""
        cat1 = self.manager.create_category("Dev")
        cat2 = self.manager.create_category("Ops")

        self.manager.create_task(title="Dev Task 1", category_id=cat1.id, priority="urgent", due_date="2026-10-01")
        self.manager.create_task(title="Dev Task 2", category_id=cat1.id, priority="low", due_date="2026-10-02")
        self.manager.create_task(title="Ops Task 1", category_id=cat2.id, priority="urgent", due_date="2026-10-03")

        # Filter by priority
        urgent_tasks = self.manager.list_tasks(priority="urgent")
        self.assertEqual(len(urgent_tasks), 2)

        # Filter by category
        dev_tasks = self.manager.list_tasks(category_id=cat1.id)
        self.assertEqual(len(dev_tasks), 2)

        # Filter by search keyword
        searched = self.manager.list_tasks(search="Ops")
        self.assertEqual(len(searched), 1)
        self.assertEqual(searched[0].title, "Ops Task 1")

    def test_update_task_status(self):
        """Test status transitions through the manager."""
        task = self.manager.create_task(title="Test Task")
        self.assertEqual(task.status, "pending")

        updated = self.manager.update_task_status(task.id, "completed")
        self.assertEqual(updated.status, "completed")

        # Check persistence
        reloaded = self.manager.get_task(task.id)
        self.assertEqual(reloaded.status, "completed")

    def test_update_task_attributes(self):
        """Test updating title, priority, due_date, and tags."""
        cat1 = self.manager.create_category("OldCat")
        cat2 = self.manager.create_category("NewCat")

        task = self.manager.create_task(
            title="Initial Title",
            category_id=cat1.id,
            priority="low",
            tags=["v1"],
        )

        updated = self.manager.update_task(
            task_id=task.id,
            title="Updated Title",
            category_id=cat2.id,
            priority="urgent",
            tags=["v2", "release"],
        )

        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.category_name, "NewCat")
        self.assertEqual(updated.priority, "urgent")
        self.assertEqual(sorted(updated.tags), ["release", "v2"])

    def test_delete_task_cascades(self):
        """Test deleting a task removes junction table records."""
        task = self.manager.create_task(title="To be deleted", tags=["temp1", "temp2"])
        task_id = task.id

        success = self.manager.delete_task(task_id)
        self.assertTrue(success)

        with self.assertRaises(TaskNotFoundError):
            self.manager.get_task(task_id)

    def test_category_duplicate_validation(self):
        """Test that duplicate category names trigger ValidationError."""
        self.manager.create_category("UniqueCategory")
        with self.assertRaises(ValidationError):
            self.manager.create_category("UniqueCategory")

    def test_delete_category_sets_null(self):
        """Test ON DELETE SET NULL behavior on tasks when category is deleted."""
        cat = self.manager.create_category("Temporary")
        task = self.manager.create_task(title="Dependent Task", category_id=cat.id)

        self.manager.delete_category(cat.id)

        # Task should still exist, but category is now Uncategorized / None
        reloaded_task = self.manager.get_task(task.id)
        self.assertIsNone(reloaded_task.category_id)
        self.assertEqual(reloaded_task.category_name, "Uncategorized")

    def test_nonexistent_ids_raise_errors(self):
        """Test that invalid IDs raise appropriate custom exceptions."""
        with self.assertRaises(TaskNotFoundError):
            self.manager.get_task(99999)

        with self.assertRaises(TaskNotFoundError):
            self.manager.delete_task(99999)

        with self.assertRaises(CategoryNotFoundError):
            self.manager.create_task(title="Invalid Cat Task", category_id=99999)


if __name__ == "__main__":
    unittest.main()
