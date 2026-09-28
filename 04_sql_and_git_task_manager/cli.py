"""Command-Line Interface (CLI) for Task Manager.

Provides a clean, interactive text interface with tabular layouts,
input validation, and user feedback.
"""

import sys
from typing import List, Optional
from datetime import date

from managers.task_manager import TaskManager
from models.category import Category
from models.exceptions import (
    CategoryNotFoundError,
    DatabaseError,
    TaskManagerError,
    TaskNotFoundError,
    ValidationError,
)
from models.task import Task
from utils.exporter import export_tasks_to_json


class TaskManagerCLI:
    """Handles terminal user interactions and formatting for the Task Manager."""

    def __init__(self, manager: Optional[TaskManager] = None) -> None:
        self.manager = manager or TaskManager()

    # -------------------------------------------------------------------------
    # Formatting Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def print_header(title: str) -> None:
        """Print stylized section header."""
        border = "=" * 70
        print(f"\n{border}")
        print(f" {title.upper()}")
        print(f"{border}")

    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None) -> None:
        """Print formatted ASCII table."""
        if not rows:
            print("  (No records found.)")
            return

        if col_widths is None:
            col_widths = []
            for i, header in enumerate(headers):
                max_len = len(header)
                for row in rows:
                    if i < len(row):
                        max_len = max(max_len, len(str(row[i])))
                col_widths.append(min(max_len + 2, 45))  # Cap column width at 45

        # Format header line
        header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
        separator = "-+-".join("-" * w for w in col_widths)

        print(header_str)
        print(separator)
        for row in rows:
            row_items = []
            for item, width in zip(row, col_widths):
                text = str(item)
                if len(text) > width:
                    text = text[: width - 3] + "..."
                row_items.append(f"{text:<{width}}")
            print(" | ".join(row_items))

    # -------------------------------------------------------------------------
    # Display Actions
    # -------------------------------------------------------------------------

    def display_tasks(self, tasks: List[Task], title: str = "Task List") -> None:
        """Render a collection of tasks in tabular view."""
        self.print_header(title)
        headers = ["ID", "Status", "Priority", "Title", "Category", "Due Date", "Tags"]
        rows = []
        for t in tasks:
            status_box = "[X]" if t.status == "completed" else ("[~]" if t.status == "in_progress" else "[ ]")
            tags_str = ", ".join(t.tags) if t.tags else "-"
            due_str = str(t.due_date) if t.due_date else "-"
            if t.is_overdue():
                due_str += " (OVERDUE)"
            rows.append([
                str(t.id),
                f"{status_box} {t.status}",
                t.priority,
                t.title,
                t.category_name,
                due_str,
                tags_str,
            ])
        self.print_table(headers, rows)
        print(f"\nTotal tasks displayed: {len(tasks)}")

    def display_categories(self, categories: List[Category]) -> None:
        """Render categories in tabular view."""
        self.print_header("Categories")
        headers = ["ID", "Name", "Tasks Count", "Description"]
        rows = [
            [str(c.id), c.name, str(c.task_count), c.description or "-"]
            for c in categories
        ]
        self.print_table(headers, rows)

    def display_analytics(self) -> None:
        """Render SQL aggregates, GROUP BY, and HAVING analytical reports."""
        self.print_header("SQL Analytics & System Metrics")

        # 1. Overall System Metrics (COUNT & MIN/MAX aggregates)
        metrics = self.manager.get_metrics_summary()
        print("\n[+] OVERALL SUMMARY (SQL Aggregates: COUNT, MIN, MAX)")
        print(f"  * Total Tasks        : {metrics['total_tasks']}")
        print(f"  * Completed Tasks    : {metrics['completed_tasks']} ({metrics['completion_rate']}%)")
        print(f"  * In Progress Tasks  : {metrics['in_progress_tasks']}")
        print(f"  * Pending Tasks      : {metrics['pending_tasks']}")
        print(f"  * Overdue Tasks      : {metrics['overdue_tasks']}")
        print(f"  * Earliest Due Date  : {metrics['earliest_due'] or 'None'}")
        print(f"  * Latest Due Date    : {metrics['latest_due'] or 'None'}")

        # 2. Category Breakdown (LEFT JOIN, GROUP BY, HAVING)
        print("\n[+] CATEGORY BREAKDOWN (SQL: LEFT JOIN, GROUP BY categories.id, categories.name)")
        cat_breakdown = self.manager.get_category_breakdown()
        headers = ["Category", "Total", "Completed", "Active", "Completion %"]
        rows = [
            [
                cb["category_name"],
                str(cb["total_tasks"]),
                str(cb["completed_tasks"]),
                str(cb["active_tasks"]),
                f"{cb['completion_rate']}%",
            ]
            for cb in cat_breakdown
        ]
        self.print_table(headers, rows)

        # 3. Priority Breakdown (GROUP BY priority)
        print("\n[+] PRIORITY DISTRIBUTION (SQL: GROUP BY priority, HAVING COUNT(*) >= 1)")
        prio_breakdown = self.manager.get_priority_breakdown()
        prio_headers = ["Priority", "Total Tasks", "Completed", "Pending"]
        prio_rows = [
            [
                pb["priority"].upper(),
                str(pb["task_count"]),
                str(pb["completed_count"]),
                str(pb["pending_count"]),
            ]
            for pb in prio_breakdown
        ]
        self.print_table(prio_headers, prio_rows)

        # 4. Overdue Tasks
        overdue = self.manager.get_overdue_tasks()
        if overdue:
            print("\n[!] OVERDUE TASKS (SQL: WHERE status != 'completed' AND due_date < CURRENT_DATE)")
            od_headers = ["ID", "Title", "Category", "Due Date", "Days Overdue"]
            od_rows = [
                [
                    str(o["id"]),
                    o["title"],
                    o["category_name"],
                    str(o["due_date"]),
                    f"{o['days_overdue']} day(s)",
                ]
                for o in overdue
            ]
            self.print_table(od_headers, od_rows)
        else:
            print("\n[✓] No tasks are currently overdue. Excellent!")

    # -------------------------------------------------------------------------
    # Interactive Prompts
    # -------------------------------------------------------------------------

    def prompt_add_task(self) -> None:
        """Prompt user to create a new task."""
        self.print_header("Add New Task")
        try:
            title = input("Task Title (required): ").strip()
            if not title:
                print("Error: Task title cannot be empty.")
                return

            description = input("Task Description (optional): ").strip() or None

            # Category selection
            categories = self.manager.list_categories()
            if categories:
                print("\nAvailable Categories:")
                for c in categories:
                    print(f"  [{c.id}] {c.name}")
                cat_input = input("Category ID (leave blank for none): ").strip()
                category_id = int(cat_input) if cat_input.isdigit() else None
            else:
                category_id = None

            print(f"\nPriorities: {', '.join(Task.VALID_PRIORITIES)}")
            priority_input = input("Priority [medium]: ").strip().lower() or "medium"

            due_input = input("Due Date (YYYY-MM-DD, optional): ").strip() or None

            tags_input = input("Tags (comma-separated, e.g., 'backend, urgent'): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

            task = self.manager.create_task(
                title=title,
                description=description,
                category_id=category_id,
                priority=priority_input,
                due_date=due_input,
                tags=tags,
            )
            print(f"\n[SUCCESS] Task #{task.id} created successfully!")
        except (ValidationError, CategoryNotFoundError) as e:
            print(f"\n[VALIDATION ERROR] {e}")
        except DatabaseError as e:
            print(f"\n[DATABASE ERROR] {e}")

    def prompt_view_task(self) -> None:
        """View detailed information for a single task."""
        self.print_header("View Task Details")
        task_id_str = input("Enter Task ID: ").strip()
        if not task_id_str.isdigit():
            print("Error: Invalid ID.")
            return

        try:
            task = self.manager.get_task(int(task_id_str))
            print(f"\n--- Task #{task.id} ---")
            print(f"Title         : {task.title}")
            print(f"Description   : {task.description or 'No description'}")
            print(f"Category      : {task.category_name} (ID: {task.category_id})")
            print(f"Status        : {task.status}")
            print(f"Priority      : {task.priority}")
            print(f"Due Date      : {task.due_date or 'No due date'}")
            if task.is_overdue():
                print(f"Overdue       : YES ({abs(task.days_remaining() or 0)} days past due)")
            elif task.due_date:
                print(f"Days Left     : {task.days_remaining()} day(s)")
            print(f"Tags          : {', '.join(task.tags) if task.tags else 'No tags'}")
            print(f"Created At    : {task.created_at}")
            print(f"Last Updated  : {task.updated_at}")
        except TaskNotFoundError as e:
            print(f"\n[NOT FOUND] {e}")
        except DatabaseError as e:
            print(f"\n[DATABASE ERROR] {e}")

    def prompt_update_status(self) -> None:
        """Prompt user to change a task's status."""
        self.print_header("Update Task Status")
        task_id_str = input("Enter Task ID: ").strip()
        if not task_id_str.isdigit():
            print("Error: Invalid ID.")
            return

        print(f"\nOptions: {', '.join(Task.VALID_STATUSES)}")
        status = input("New Status: ").strip().lower()
        try:
            task = self.manager.update_task_status(int(task_id_str), status)
            print(f"\n[SUCCESS] Task #{task.id} status changed to '{task.status}'.")
        except (TaskNotFoundError, ValidationError) as e:
            print(f"\n[ERROR] {e}")
        except DatabaseError as e:
            print(f"\n[DATABASE ERROR] {e}")

    def prompt_delete_task(self) -> None:
        """Prompt user to delete a task."""
        self.print_header("Delete Task")
        task_id_str = input("Enter Task ID to delete: ").strip()
        if not task_id_str.isdigit():
            print("Error: Invalid ID.")
            return

        confirm = input(f"Are you sure you want to delete task #{task_id_str}? (y/N): ").strip().lower()
        if confirm == "y":
            try:
                self.manager.delete_task(int(task_id_str))
                print(f"\n[SUCCESS] Task #{task_id_str} deleted successfully.")
            except TaskNotFoundError as e:
                print(f"\n[ERROR] {e}")
            except DatabaseError as e:
                print(f"\n[DATABASE ERROR] {e}")
        else:
            print("Deletion canceled.")

    def prompt_manage_categories(self) -> None:
        """Menu for managing categories."""
        while True:
            self.print_header("Category Management")
            print("1. List All Categories")
            print("2. Create New Category")
            print("3. Delete Category")
            print("0. Back to Main Menu")

            choice = input("\nSelect Option [0-3]: ").strip()
            if choice == "1":
                cats = self.manager.list_categories()
                self.display_categories(cats)
            elif choice == "2":
                name = input("Category Name: ").strip()
                desc = input("Category Description (optional): ").strip() or None
                try:
                    cat = self.manager.create_category(name, desc)
                    print(f"\n[SUCCESS] Category #{cat.id} '{cat.name}' created.")
                except (ValidationError, DatabaseError) as e:
                    print(f"\n[ERROR] {e}")
            elif choice == "3":
                cat_id_str = input("Enter Category ID to delete: ").strip()
                if cat_id_str.isdigit():
                    confirm = input(f"Delete category #{cat_id_str}? Tasks will be uncategorized (y/N): ").lower()
                    if confirm == "y":
                        try:
                            self.manager.delete_category(int(cat_id_str))
                            print(f"\n[SUCCESS] Category #{cat_id_str} deleted.")
                        except (CategoryNotFoundError, DatabaseError) as e:
                            print(f"\n[ERROR] {e}")
            elif choice == "0":
                break

    def prompt_export_json(self) -> None:
        """Prompt to export tasks to structured JSON."""
        self.print_header("Export Tasks to JSON")
        filename = input("Enter output filename [tasks_export.json]: ").strip() or "tasks_export.json"
        try:
            path = export_tasks_to_json(self.manager, filename)
            print(f"\n[SUCCESS] Tasks successfully exported to:\n  {path}")
        except Exception as e:
            print(f"\n[ERROR] Export failed: {e}")

    # -------------------------------------------------------------------------
    # Main Loop
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """Main CLI loop."""
        while True:
            self.print_header("CLI Task Manager - PostgreSQL Backend")
            print("1. List All Tasks")
            print("2. Filter / Search Tasks")
            print("3. Add New Task")
            print("4. View Task Details")
            print("5. Update Task Status")
            print("6. Delete Task")
            print("7. Category Management")
            print("8. SQL Analytics & Reports (GROUP BY, HAVING)")
            print("9. Export Tasks to JSON")
            print("0. Exit")

            choice = input("\nSelect an option [0-9]: ").strip()

            if choice == "1":
                tasks = self.manager.list_tasks()
                self.display_tasks(tasks, "All Tasks")
            elif choice == "2":
                print("\nFilter options (press enter to skip filter):")
                st = input("Status (pending/in_progress/completed): ").strip() or None
                pr = input("Priority (low/medium/high/urgent): ").strip() or None
                kw = input("Search Keyword (title/description): ").strip() or None
                tasks = self.manager.list_tasks(status=st, priority=pr, search=kw)
                self.display_tasks(tasks, "Filtered Tasks")
            elif choice == "3":
                self.prompt_add_task()
            elif choice == "4":
                self.prompt_view_task()
            elif choice == "5":
                self.prompt_update_status()
            elif choice == "6":
                self.prompt_delete_task()
            elif choice == "7":
                self.prompt_manage_categories()
            elif choice == "8":
                self.display_analytics()
            elif choice == "9":
                self.prompt_export_json()
            elif choice == "0":
                print("\nExiting Task Manager. Goodbye!\n")
                break
            else:
                print("Invalid option. Please choose between 0 and 9.")
