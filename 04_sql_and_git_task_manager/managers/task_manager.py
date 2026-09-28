"""TaskManager: Business logic coordinator and PostgreSQL query orchestrator.

Implements clean OOP architecture, relational JOINs, GROUP BY/HAVING aggregations,
and robust runtime error handling with custom domain exceptions.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
import psycopg2

from database.connection import DatabaseConnection, get_db_connection
from models.category import Category
from models.exceptions import (
    CategoryNotFoundError,
    DatabaseError,
    TaskManagerError,
    TaskNotFoundError,
    ValidationError,
)
from models.task import Task
from utils.logger import setup_logger

logger = setup_logger("TaskManager.Manager")


class TaskManager:
    """Coordinates Task and Category business operations over PostgreSQL."""

    def __init__(self, db: Optional[DatabaseConnection] = None) -> None:
        """Initialize manager with database connection."""
        self.db = db or get_db_connection()

    # =========================================================================
    # Task Operations
    # =========================================================================

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        priority: str = "medium",
        due_date: Optional[Union[date, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """Create and persist a new Task with optional category and tags."""
        # Domain validation via Task constructor
        task = Task(
            title=title,
            description=description,
            category_id=category_id,
            priority=priority,
            due_date=due_date,
            tags=tags,
        )

        try:
            with self.db.get_cursor() as cur:
                # Validate category existence if provided
                if task.category_id:
                    cur.execute("SELECT id, name FROM categories WHERE id = %s;", (task.category_id,))
                    cat_row = cur.fetchone()
                    if not cat_row:
                        raise CategoryNotFoundError(f"Category ID {task.category_id} does not exist.")
                    task.category_name = cat_row["name"]

                # Insert Task
                insert_task_sql = """
                    INSERT INTO tasks (title, description, category_id, status, priority, due_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at, updated_at;
                """
                cur.execute(
                    insert_task_sql,
                    (
                        task.title,
                        task.description,
                        task.category_id,
                        task.status,
                        task.priority,
                        task.due_date,
                    ),
                )
                row = cur.fetchone()
                task.id = row["id"]
                task.created_at = row["created_at"]
                task.updated_at = row["updated_at"]

                # Handle Tags (Many-to-Many via task_tags junction table)
                if task.tags:
                    for tag_name in task.tags:
                        tag_clean = tag_name.strip().lower()
                        if not tag_clean:
                            continue
                        # Upsert tag into tags table
                        cur.execute(
                            """
                            INSERT INTO tags (name) VALUES (%s)
                            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                            RETURNING id;
                            """,
                            (tag_clean,),
                        )
                        tag_id = cur.fetchone()["id"]
                        # Link in task_tags
                        cur.execute(
                            """
                            INSERT INTO task_tags (task_id, tag_id)
                            VALUES (%s, %s)
                            ON CONFLICT (task_id, tag_id) DO NOTHING;
                            """,
                            (task.id, tag_id),
                        )

            logger.info("Created Task ID %d: '%s'", task.id, task.title)
            return task
        except psycopg2.Error as e:
            logger.error("Database error while creating task: %s", e)
            raise DatabaseError(f"Failed to create task: {e}") from e

    def get_task(self, task_id: int) -> Task:
        """Retrieve a single Task by ID with category and tags via Relational JOINs."""
        sql = """
            SELECT 
                t.id,
                t.title,
                t.description,
                t.category_id,
                c.name AS category_name,
                t.status,
                t.priority,
                t.due_date,
                t.created_at,
                t.updated_at,
                COALESCE(STRING_AGG(tg.name, ',' ORDER BY tg.name), '') AS tags
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            WHERE t.id = %s
            GROUP BY t.id, c.name;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql, (task_id,))
                row = cur.fetchone()
                if not row:
                    raise TaskNotFoundError(f"Task with ID {task_id} not found.")
                return Task.from_row(row)
        except psycopg2.Error as e:
            logger.error("Database error while fetching task %d: %s", task_id, e)
            raise DatabaseError(f"Failed to fetch task {task_id}: {e}") from e

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "id",
    ) -> List[Task]:
        """List tasks matching filter conditions with Category and Tag JOINs."""
        base_sql = """
            SELECT 
                t.id,
                t.title,
                t.description,
                t.category_id,
                COALESCE(c.name, 'Uncategorized') AS category_name,
                t.status,
                t.priority,
                t.due_date,
                t.created_at,
                t.updated_at,
                COALESCE(STRING_AGG(tg.name, ',' ORDER BY tg.name), '') AS tags
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
        """
        where_clauses = []
        params = []

        if status:
            where_clauses.append("t.status = %s")
            params.append(status.lower().strip())

        if priority:
            where_clauses.append("t.priority = %s")
            params.append(priority.lower().strip())

        if category_id:
            where_clauses.append("t.category_id = %s")
            params.append(category_id)

        if search:
            where_clauses.append("(t.title ILIKE %s OR t.description ILIKE %s)")
            wildcard = f"%{search.strip()}%"
            params.extend([wildcard, wildcard])

        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        base_sql += " GROUP BY t.id, c.name"

        # Sorting validation
        allowed_sorts = {
            "id": "t.id ASC",
            "due_date": "t.due_date ASC NULLS LAST",
            "priority": """
                CASE t.priority 
                    WHEN 'urgent' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                END ASC
            """,
            "title": "t.title ASC",
        }
        order_clause = allowed_sorts.get(sort_by, "t.id ASC")
        base_sql += f" ORDER BY {order_clause};"

        try:
            with self.db.get_cursor() as cur:
                cur.execute(base_sql, tuple(params))
                rows = cur.fetchall()
                return [Task.from_row(r) for r in rows]
        except psycopg2.Error as e:
            logger.error("Database error while listing tasks: %s", e)
            raise DatabaseError(f"Failed to list tasks: {e}") from e

    def update_task_status(self, task_id: int, new_status: str) -> Task:
        """Update lifecycle status of a task."""
        # Validate status value
        test_task = Task(title="test", status=new_status)

        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    """
                    UPDATE tasks 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    RETURNING id;
                    """,
                    (test_task.status, task_id),
                )
                if not cur.fetchone():
                    raise TaskNotFoundError(f"Task with ID {task_id} not found.")

            logger.info("Updated status for Task %d to '%s'", task_id, test_task.status)
            return self.get_task(task_id)
        except psycopg2.Error as e:
            logger.error("Database error updating status for task %d: %s", task_id, e)
            raise DatabaseError(f"Failed to update task status: {e}") from e

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        priority: Optional[str] = None,
        due_date: Optional[Union[date, str]] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """Update multiple task attributes in a single transaction."""
        existing = self.get_task(task_id)

        # Apply new attributes or preserve existing
        new_title = title if title is not None else existing.title
        new_desc = description if description is not None else existing.description
        new_cat = category_id if category_id is not None else existing.category_id
        new_priority = priority if priority is not None else existing.priority
        new_due = due_date if due_date is not None else existing.due_date
        new_status = status if status is not None else existing.status

        # Validate through Task model
        updated_model = Task(
            title=new_title,
            description=new_desc,
            category_id=new_cat,
            priority=new_priority,
            due_date=new_due,
            status=new_status,
        )

        try:
            with self.db.get_cursor() as cur:
                if updated_model.category_id:
                    cur.execute("SELECT id FROM categories WHERE id = %s;", (updated_model.category_id,))
                    if not cur.fetchone():
                        raise CategoryNotFoundError(f"Category ID {updated_model.category_id} not found.")

                cur.execute(
                    """
                    UPDATE tasks
                    SET title = %s,
                        description = %s,
                        category_id = %s,
                        priority = %s,
                        due_date = %s,
                        status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        updated_model.title,
                        updated_model.description,
                        updated_model.category_id,
                        updated_model.priority,
                        updated_model.due_date,
                        updated_model.status,
                        task_id,
                    ),
                )

                # Update tags if provided
                if tags is not None:
                    # Remove old tag associations
                    cur.execute("DELETE FROM task_tags WHERE task_id = %s;", (task_id,))
                    for tname in tags:
                        tclean = tname.strip().lower()
                        if not tclean:
                            continue
                        cur.execute(
                            """
                            INSERT INTO tags (name) VALUES (%s)
                            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                            RETURNING id;
                            """,
                            (tclean,),
                        )
                        tid = cur.fetchone()["id"]
                        cur.execute(
                            "INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s);",
                            (task_id, tid),
                        )

            logger.info("Successfully updated Task ID %d", task_id)
            return self.get_task(task_id)
        except psycopg2.Error as e:
            logger.error("Database error updating task %d: %s", task_id, e)
            raise DatabaseError(f"Failed to update task: {e}") from e

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID. Cascades to task_tags junction table."""
        try:
            with self.db.get_cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
                row = cur.fetchone()
                if not row:
                    raise TaskNotFoundError(f"Task with ID {task_id} not found.")
            logger.info("Deleted Task ID %d", task_id)
            return True
        except psycopg2.Error as e:
            logger.error("Database error deleting task %d: %s", task_id, e)
            raise DatabaseError(f"Failed to delete task: {e}") from e

    # =========================================================================
    # Category Operations
    # =========================================================================

    def create_category(self, name: str, description: Optional[str] = None) -> Category:
        """Create a new category."""
        category = Category(name=name, description=description)
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO categories (name, description)
                    VALUES (%s, %s)
                    RETURNING id, created_at;
                    """,
                    (category.name, category.description),
                )
                row = cur.fetchone()
                category.id = row["id"]
                category.created_at = row["created_at"]
            logger.info("Created Category ID %d: '%s'", category.id, category.name)
            return category
        except psycopg2.IntegrityError as e:
            logger.warning("Category '%s' already exists: %s", category.name, e)
            raise ValidationError(f"Category '{category.name}' already exists.") from e
        except psycopg2.Error as e:
            logger.error("Database error creating category: %s", e)
            raise DatabaseError(f"Failed to create category: {e}") from e

    def list_categories(self) -> List[Category]:
        """List all categories with task count via LEFT JOIN and GROUP BY."""
        sql = """
            SELECT 
                c.id,
                c.name,
                c.description,
                c.created_at,
                COUNT(t.id) AS task_count
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            GROUP BY c.id, c.name, c.description, c.created_at
            ORDER BY c.id ASC;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return [Category.from_row(r) for r in rows]
        except psycopg2.Error as e:
            logger.error("Database error listing categories: %s", e)
            raise DatabaseError(f"Failed to list categories: {e}") from e

    def delete_category(self, category_id: int) -> bool:
        """Delete a category. Associated tasks will have category_id set to NULL."""
        try:
            with self.db.get_cursor() as cur:
                cur.execute("DELETE FROM categories WHERE id = %s RETURNING id;", (category_id,))
                if not cur.fetchone():
                    raise CategoryNotFoundError(f"Category with ID {category_id} not found.")
            logger.info("Deleted Category ID %d", category_id)
            return True
        except psycopg2.Error as e:
            logger.error("Database error deleting category %d: %s", category_id, e)
            raise DatabaseError(f"Failed to delete category: {e}") from e

    # =========================================================================
    # SQL Foundations: Advanced Analytics (GROUP BY, HAVING, Aggregate Funcs)
    # =========================================================================

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Aggregate metrics using COUNT and conditional expressions."""
        sql = """
            SELECT 
                COUNT(*) AS total_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_tasks,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) AS in_progress_tasks,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending_tasks,
                COUNT(CASE WHEN status != 'completed' AND due_date < CURRENT_DATE THEN 1 END) AS overdue_tasks,
                MIN(due_date) AS earliest_due,
                MAX(due_date) AS latest_due
            FROM tasks;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                total = row["total_tasks"]
                completed = row["completed_tasks"]
                rate = round((completed / total * 100), 1) if total > 0 else 0.0

                return {
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "in_progress_tasks": row["in_progress_tasks"],
                    "pending_tasks": row["pending_tasks"],
                    "overdue_tasks": row["overdue_tasks"],
                    "completion_rate": rate,
                    "earliest_due": str(row["earliest_due"]) if row["earliest_due"] else None,
                    "latest_due": str(row["latest_due"]) if row["latest_due"] else None,
                }
        except psycopg2.Error as e:
            logger.error("Database error fetching metrics: %s", e)
            raise DatabaseError(f"Failed to calculate metrics: {e}") from e

    def get_category_breakdown(self, min_tasks: int = 0) -> List[Dict[str, Any]]:
        """Category breakdown using LEFT JOIN, GROUP BY, and HAVING clause.
        
        Demonstrates:
        - Relational LEFT JOIN to retain categories even with 0 tasks
        - GROUP BY categories.id, categories.name
        - HAVING COUNT(t.id) >= min_tasks to filter aggregated groups
        """
        sql = """
            SELECT 
                c.id AS category_id,
                c.name AS category_name,
                COUNT(t.id) AS total_tasks,
                COUNT(CASE WHEN t.status = 'completed' THEN 1 END) AS completed_tasks,
                COUNT(CASE WHEN t.status != 'completed' THEN 1 END) AS active_tasks
            FROM categories c
            LEFT JOIN tasks t ON c.id = t.category_id
            GROUP BY c.id, c.name
            HAVING COUNT(t.id) >= %s
            ORDER BY total_tasks DESC, c.name ASC;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql, (min_tasks,))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    tot = r["total_tasks"]
                    comp = r["completed_tasks"]
                    rate = round((comp / tot * 100), 1) if tot > 0 else 0.0
                    results.append({
                        "category_id": r["category_id"],
                        "category_name": r["category_name"],
                        "total_tasks": tot,
                        "completed_tasks": comp,
                        "active_tasks": r["active_tasks"],
                        "completion_rate": rate,
                    })
                return results
        except psycopg2.Error as e:
            logger.error("Database error getting category breakdown: %s", e)
            raise DatabaseError(f"Failed to fetch category breakdown: {e}") from e

    def get_priority_breakdown(self, min_count: int = 1) -> List[Dict[str, Any]]:
        """Priority distribution using GROUP BY and HAVING."""
        sql = """
            SELECT 
                priority,
                COUNT(*) AS task_count,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_count,
                COUNT(CASE WHEN status != 'completed' THEN 1 END) AS pending_count
            FROM tasks
            GROUP BY priority
            HAVING COUNT(*) >= %s
            ORDER BY 
                CASE priority 
                    WHEN 'urgent' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                END;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql, (min_count,))
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except psycopg2.Error as e:
            logger.error("Database error getting priority breakdown: %s", e)
            raise DatabaseError(f"Failed to fetch priority breakdown: {e}") from e

    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Fetch tasks where due_date < CURRENT_DATE and status is not completed."""
        sql = """
            SELECT 
                t.id,
                t.title,
                t.status,
                t.priority,
                t.due_date,
                COALESCE(c.name, 'Uncategorized') AS category_name,
                (CURRENT_DATE - t.due_date) AS days_overdue
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.status != 'completed' AND t.due_date < CURRENT_DATE
            ORDER BY t.due_date ASC;
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                results = []
                for r in rows:
                    d = dict(r)
                    if d.get("due_date"):
                        d["due_date"] = str(d["due_date"])
                    results.append(d)
                return results
        except psycopg2.Error as e:
            logger.error("Database error getting overdue tasks: %s", e)
            raise DatabaseError(f"Failed to fetch overdue tasks: {e}") from e
