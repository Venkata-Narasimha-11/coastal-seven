"""Database Seeder: Populates the PostgreSQL database with realistic sample data."""

import sys
from datetime import date, timedelta
from pathlib import Path

# Add project root to sys.path so modules can be imported directly
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.connection import get_db_connection
from utils.logger import setup_logger

logger = setup_logger("TaskManager.Seed")


def seed_database() -> None:
    """Initialize schema and seed sample categories, tasks, tags, and relations."""
    db = get_db_connection()
    logger.info("Initializing schema prior to seeding...")
    db.init_schema()

    today = date.today()

    with db.get_cursor() as cur:
        logger.info("Seeding categories...")
        categories_data = [
            ("Work", "Professional engineering tasks and project milestones"),
            ("Study", "Learning Python, SQL, Git, and software architecture"),
            ("Personal", "Daily personal habits, health, and routines"),
            ("Finance", "Tax planning, budget audits, and investments"),
            ("Empty Category", "Category created intentionally without tasks to test LEFT JOIN"),
        ]
        category_ids = {}
        for name, desc in categories_data:
            cur.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id;",
                (name, desc),
            )
            category_ids[name] = cur.fetchone()["id"]

        logger.info("Seeding tags...")
        tags_data = ["backend", "database", "git", "bug", "feature", "documentation", "urgent"]
        tag_ids = {}
        for tag_name in tags_data:
            cur.execute(
                "INSERT INTO tags (name) VALUES (%s) RETURNING id;",
                (tag_name,),
            )
            tag_ids[tag_name] = cur.fetchone()["id"]

        logger.info("Seeding tasks...")
        tasks_data = [
            (
                "Design PostgreSQL Schema",
                "Create tables for tasks, categories, and tags with indexes and foreign keys.",
                category_ids["Work"],
                "completed",
                "high",
                today - timedelta(days=2),
                ["backend", "database"],
            ),
            (
                "Implement Task and TaskManager OOP Classes",
                "Encapsulate domain models and business logic with unit testing.",
                category_ids["Work"],
                "in_progress",
                "urgent",
                today + timedelta(days=1),
                ["backend", "feature"],
            ),
            (
                "Write Complex SQL Queries with JOINs & HAVING",
                "Practice INNER JOIN, LEFT JOIN, GROUP BY, and HAVING aggregate filters.",
                category_ids["Study"],
                "in_progress",
                "high",
                today + timedelta(days=2),
                ["database", "documentation"],
            ),
            (
                "Fix Bug in JSON Exporter Serialization",
                "Ensure datetime and date objects serialize cleanly to standard ISO format.",
                category_ids["Work"],
                "pending",
                "medium",
                today - timedelta(days=1),  # Overdue task
                ["bug", "backend"],
            ),
            (
                "Practice Git Branching and GitHub Flow",
                "Create feature branches, perform systematic commits, and handle PR merges.",
                category_ids["Study"],
                "completed",
                "medium",
                today - timedelta(days=3),
                ["git", "documentation"],
            ),
            (
                "Complete Weekly Gym Workout Plan",
                "Complete 4 strength sessions and 2 cardio recovery walks.",
                category_ids["Personal"],
                "in_progress",
                "medium",
                today + timedelta(days=3),
                [],
            ),
            (
                "Quarterly Budget & Expense Review",
                "Categorize monthly bank statements and reconcile tax receipts.",
                category_ids["Finance"],
                "pending",
                "low",
                today + timedelta(days=7),
                [],
            ),
            (
                "Review Peer Pull Request for CLI Interface",
                "Check CLI error handling, command arguments, and table presentation.",
                category_ids["Work"],
                "pending",
                "urgent",
                today,
                ["feature", "urgent"],
            ),
        ]

        for title, desc, cat_id, status, priority, due_date, task_tag_names in tasks_data:
            cur.execute(
                """
                INSERT INTO tasks (title, description, category_id, status, priority, due_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (title, desc, cat_id, status, priority, due_date),
            )
            task_id = cur.fetchone()["id"]

            for tname in task_tag_names:
                cur.execute(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s);",
                    (task_id, tag_ids[tname]),
                )

    logger.info("Database seeding successfully completed with %d tasks!", len(tasks_data))


if __name__ == "__main__":
    seed_database()
