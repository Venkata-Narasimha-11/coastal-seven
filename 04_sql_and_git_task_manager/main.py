"""Main application entry point for CLI Task Manager.

Supports both interactive menu mode and direct command-line arguments.
"""

import argparse
import sys
from pathlib import Path

# Ensure root package directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from cli import TaskManagerCLI
from database.connection import get_db_connection
from database.seed import seed_database
from managers.task_manager import TaskManager
from utils.exporter import export_tasks_to_json
from utils.logger import setup_logger

logger = setup_logger("TaskManager.Main")


def parse_arguments() -> argparse.Namespace:
    """Parse command line flags and options."""
    parser = argparse.ArgumentParser(
        description="CLI Task Manager - Python OOP + PostgreSQL Persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all tasks in tabular view",
    )
    parser.add_argument(
        "--add",
        type=str,
        metavar="TITLE",
        help="Quickly add a task with the given title",
    )
    parser.add_argument(
        "--desc",
        type=str,
        default=None,
        metavar="DESC",
        help="Description for the new task (used with --add)",
    )
    parser.add_argument(
        "--priority",
        type=str,
        default="medium",
        choices=["low", "medium", "high", "urgent"],
        help="Task priority level (default: medium)",
    )
    parser.add_argument(
        "--due",
        type=str,
        default=None,
        metavar="YYYY-MM-DD",
        help="Due date in YYYY-MM-DD format (used with --add)",
    )
    parser.add_argument(
        "--category",
        type=int,
        default=None,
        metavar="CAT_ID",
        help="Category ID for new task or filter",
    )
    parser.add_argument(
        "--status",
        type=str,
        default=None,
        choices=["pending", "in_progress", "completed", "archived"],
        help="Status filter for listing tasks",
    )
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Display SQL analytics and metrics breakdown",
    )
    parser.add_argument(
        "--export",
        type=str,
        nargs="?",
        const="tasks_export.json",
        metavar="FILENAME",
        help="Export tasks and metrics to structured JSON",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Reset and re-seed database with sample data",
    )

    return parser.parse_args()


def main() -> None:
    """Entry point execution routine."""
    args = parse_arguments()
    db = get_db_connection()

    # Verify connectivity
    try:
        if not db.ping():
            logger.error("Could not reach PostgreSQL. Please verify database is running.")
            print("\n[ERROR] Could not connect to PostgreSQL database.")
            print("Ensure PostgreSQL is running on port 5433 or configured in .env.")
            print("Run '.\\start_pg.ps1' to start the local database daemon.\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}\n")
        sys.exit(1)

    manager = TaskManager(db)
    cli = TaskManagerCLI(manager)

    # Handle direct command line flags
    if args.seed:
        print("Seeding database with sample records...")
        seed_database()
        print("Database successfully seeded.")
        return

    if args.add:
        try:
            task = manager.create_task(
                title=args.add,
                description=args.desc,
                category_id=args.category,
                priority=args.priority,
                due_date=args.due,
            )
            print(f"[SUCCESS] Created Task #{task.id}: '{task.title}' [{task.priority}]")
        except Exception as e:
            print(f"[ERROR] Failed to add task: {e}")
        return

    if args.list:
        tasks = manager.list_tasks(status=args.status, category_id=args.category)
        cli.display_tasks(tasks, "Task List")
        return

    if args.analytics:
        cli.display_analytics()
        return

    if args.export is not None:
        try:
            path = export_tasks_to_json(manager, args.export, status_filter=args.status)
            print(f"[SUCCESS] Exported tasks to: {path}")
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")
        return

    # Default: Run interactive menu
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nOperation aborted by user. Exiting.\n")


if __name__ == "__main__":
    main()
