"""Unit and verification tests for SQL queries, JOINs, GROUP BY, and HAVING."""

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


class TestSQLQueriesAndJoins(unittest.TestCase):
    """Test suite directly validating SQL Relational Queries, JOINs, and Aggregates."""

    @classmethod
    def setUpClass(cls):
        """Prepare database connection and schema."""
        cls.db = get_db_connection()
        cls.db.init_schema()
        cls.manager = TaskManager(cls.db)

    def setUp(self):
        """Seed controlled test dataset."""
        with self.db.get_cursor(dict_cursor=False) as cur:
            cur.execute("TRUNCATE task_tags, tags, tasks, categories RESTART IDENTITY CASCADE;")

        self.today = date.today()

        # Create 3 categories: Work (3 tasks), Study (1 task), Empty (0 tasks)
        self.cat_work = self.manager.create_category("Work", "Office tasks")
        self.cat_study = self.manager.create_category("Study", "Learning tasks")
        self.cat_empty = self.manager.create_category("Empty", "Unused category")

        # Create tasks with specific statuses, priorities, and dates
        self.t1 = self.manager.create_task(
            title="Work Task 1", category_id=self.cat_work.id, priority="urgent", due_date=self.today - timedelta(days=2)
        )
        self.manager.update_task_status(self.t1.id, "completed")

        self.t2 = self.manager.create_task(
            title="Work Task 2", category_id=self.cat_work.id, priority="high", due_date=self.today + timedelta(days=3)
        )
        self.manager.update_task_status(self.t2.id, "in_progress")

        self.t3 = self.manager.create_task(
            title="Work Task 3", category_id=self.cat_work.id, priority="medium", due_date=self.today - timedelta(days=1)
        )
        # Leaves t3 as pending (and OVERDUE since due_date < today)

        self.t4 = self.manager.create_task(
            title="Study Task 1", category_id=self.cat_study.id, priority="urgent", due_date=self.today + timedelta(days=5)
        )
        self.manager.update_task_status(self.t4.id, "completed")

    def test_left_join_preserves_empty_categories(self):
        """Test that LEFT JOIN returns categories with 0 tasks (e.g. Empty)."""
        categories = self.manager.list_categories()
        cat_dict = {c.name: c.task_count for c in categories}

        self.assertEqual(cat_dict["Work"], 3)
        self.assertEqual(cat_dict["Study"], 1)
        self.assertEqual(cat_dict["Empty"], 0)

    def test_group_by_having_filtering(self):
        """Test GROUP BY with HAVING clause filters aggregated categories."""
        # When min_tasks=2, only 'Work' (3 tasks) should be returned
        filtered_breakdown = self.manager.get_category_breakdown(min_tasks=2)
        names = [item["category_name"] for item in filtered_breakdown]
        self.assertIn("Work", names)
        self.assertNotIn("Study", names)
        self.assertNotIn("Empty", names)

        # When min_tasks=0, all categories returned
        all_breakdown = self.manager.get_category_breakdown(min_tasks=0)
        self.assertEqual(len(all_breakdown), 3)

    def test_aggregate_metrics(self):
        """Test aggregate calculations (total, completed, completion_rate)."""
        metrics = self.manager.get_metrics_summary()

        self.assertEqual(metrics["total_tasks"], 4)
        self.assertEqual(metrics["completed_tasks"], 2)
        self.assertEqual(metrics["in_progress_tasks"], 1)
        self.assertEqual(metrics["pending_tasks"], 1)
        self.assertEqual(metrics["overdue_tasks"], 1)
        self.assertEqual(metrics["completion_rate"], 50.0)

    def test_priority_breakdown_aggregates(self):
        """Test GROUP BY priority grouping."""
        prio_stats = self.manager.get_priority_breakdown(min_count=1)
        prio_map = {p["priority"]: p["task_count"] for p in prio_stats}

        self.assertEqual(prio_map["urgent"], 2)  # Work Task 1, Study Task 1
        self.assertEqual(prio_map["high"], 1)    # Work Task 2
        self.assertEqual(prio_map["medium"], 1)  # Work Task 3

    def test_overdue_tasks_query(self):
        """Test overdue tasks logic: status != 'completed' AND due_date < CURRENT_DATE."""
        overdue = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0]["title"], "Work Task 3")
        self.assertGreaterEqual(overdue[0]["days_overdue"], 1)


if __name__ == "__main__":
    unittest.main()
