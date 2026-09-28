"""Unit tests for JSON Exporter."""

import json
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.connection import get_db_connection
from managers.task_manager import TaskManager
from utils.exporter import export_tasks_to_json


class TestJSONExporter(unittest.TestCase):
    """Test suite validating JSON export structure and metadata."""

    @classmethod
    def setUpClass(cls):
        cls.db = get_db_connection()
        cls.db.init_schema()
        cls.manager = TaskManager(cls.db)

    def setUp(self):
        with self.db.get_cursor(dict_cursor=False) as cur:
            cur.execute("TRUNCATE task_tags, tags, tasks, categories RESTART IDENTITY CASCADE;")

        cat = self.manager.create_category("TestCategory")
        self.manager.create_task(
            title="Export Test Task",
            category_id=cat.id,
            priority="high",
            due_date="2026-10-20",
            tags=["json", "test"],
        )
        self.test_export_file = BASE_DIR / "exports" / "test_run_export.json"

    def tearDown(self):
        if self.test_export_file.exists():
            self.test_export_file.unlink()

    def test_export_structure(self):
        """Test that exported JSON contains all required metadata and arrays."""
        out_path = export_tasks_to_json(self.manager, self.test_export_file)
        self.assertTrue(out_path.exists())

        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("metrics_summary", data)
        self.assertIn("category_breakdown", data)
        self.assertIn("priority_distribution", data)
        self.assertIn("tasks", data)

        self.assertEqual(data["metadata"]["total_exported"], 1)
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["title"], "Export Test Task")
        self.assertEqual(data["tasks"][0]["category_name"], "TestCategory")


if __name__ == "__main__":
    unittest.main()
