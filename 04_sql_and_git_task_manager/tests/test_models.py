"""Unit tests for Domain Models (Task, Category, Exceptions)."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.category import Category
from models.exceptions import ValidationError
from models.task import Task


class TestTaskModel(unittest.TestCase):
    """Test suite for the Task domain model."""

    def test_task_creation_valid(self):
        """Test instantiating a Task with valid attributes."""
        t = Task(
            title="Complete project documentation",
            description="Write comprehensive README and docstrings",
            priority="high",
            status="pending",
            due_date="2026-10-15",
            tags=["docs", "backend"],
        )
        self.assertEqual(t.title, "Complete project documentation")
        self.assertEqual(t.priority, "high")
        self.assertEqual(t.status, "pending")
        self.assertEqual(t.due_date, date(2026, 10, 15))
        self.assertEqual(t.tags, ["docs", "backend"])

    def test_task_title_validation(self):
        """Test title validation for empty strings and length limits."""
        with self.assertRaises(ValidationError):
            Task(title="")

        with self.assertRaises(ValidationError):
            Task(title="   ")

        with self.assertRaises(ValidationError):
            Task(title="A" * 201)

    def test_task_status_validation(self):
        """Test status validation against allowed values."""
        with self.assertRaises(ValidationError):
            Task(title="Valid title", status="invalid_status")

        # Case insensitivity test
        t = Task(title="Valid title", status="COMPLETED")
        self.assertEqual(t.status, "completed")

    def test_task_priority_validation(self):
        """Test priority validation against allowed values."""
        with self.assertRaises(ValidationError):
            Task(title="Valid title", priority="critical")  # Allowed: low, medium, high, urgent

        t = Task(title="Valid title", priority="URGENT")
        self.assertEqual(t.priority, "urgent")

    def test_task_due_date_validation(self):
        """Test date parsing and format enforcement."""
        # Valid date string
        t = Task(title="Valid title", due_date="2026-12-31")
        self.assertEqual(t.due_date, date(2026, 12, 31))

        # Valid date object
        today = date.today()
        t2 = Task(title="Valid title", due_date=today)
        self.assertEqual(t2.due_date, today)

        # Invalid format
        with self.assertRaises(ValidationError):
            Task(title="Valid title", due_date="31-12-2026")

        with self.assertRaises(ValidationError):
            Task(title="Valid title", due_date="tomorrow")

    def test_state_transitions(self):
        """Test lifecycle state transition methods."""
        t = Task(title="Pipeline build")
        self.assertEqual(t.status, "pending")

        t.mark_in_progress()
        self.assertEqual(t.status, "in_progress")

        t.mark_completed()
        self.assertEqual(t.status, "completed")

        t.mark_pending()
        self.assertEqual(t.status, "pending")

    def test_overdue_detection(self):
        """Test is_overdue and days_remaining calculations."""
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        t_overdue = Task(title="Overdue task", due_date=yesterday, status="pending")
        self.assertTrue(t_overdue.is_overdue())
        self.assertEqual(t_overdue.days_remaining(), -1)

        # Completed tasks should not be considered overdue even if due date passed
        t_completed = Task(title="Done task", due_date=yesterday, status="completed")
        self.assertFalse(t_completed.is_overdue())

        t_future = Task(title="Future task", due_date=tomorrow, status="pending")
        self.assertFalse(t_future.is_overdue())
        self.assertEqual(t_future.days_remaining(), 1)

    def test_serialization_to_dict(self):
        """Test dictionary serialization contains expected keys."""
        t = Task(
            task_id=42,
            title="Export data",
            category_name="Database",
            priority="high",
            due_date=date(2026, 10, 1),
            tags=["sql", "json"],
        )
        d = t.to_dict()
        self.assertEqual(d["id"], 42)
        self.assertEqual(d["title"], "Export data")
        self.assertEqual(d["category_name"], "Database")
        self.assertEqual(d["due_date"], "2026-10-01")
        self.assertEqual(d["tags"], ["sql", "json"])
        self.assertIn("is_overdue", d)


class TestCategoryModel(unittest.TestCase):
    """Test suite for Category domain model."""

    def test_category_creation_valid(self):
        """Test valid category instantiation."""
        cat = Category(name="Backend Engineering", description="API and DB work")
        self.assertEqual(cat.name, "Backend Engineering")
        self.assertEqual(cat.description, "API and DB work")

    def test_category_name_validation(self):
        """Test validation on empty name or excessive length."""
        with self.assertRaises(ValidationError):
            Category(name="")

        with self.assertRaises(ValidationError):
            Category(name="   ")

        with self.assertRaises(ValidationError):
            Category(name="X" * 51)

    def test_category_serialization(self):
        """Test category dictionary serialization."""
        cat = Category(category_id=7, name="Finance", task_count=5)
        d = cat.to_dict()
        self.assertEqual(d["id"], 7)
        self.assertEqual(d["name"], "Finance")
        self.assertEqual(d["task_count"], 5)


if __name__ == "__main__":
    unittest.main()
