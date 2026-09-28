"""Task Domain Model."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from models.exceptions import ValidationError


class Task:
    """Represents a discrete unit of work or actionable task."""

    VALID_STATUSES = ("pending", "in_progress", "completed", "archived")
    VALID_PRIORITIES = ("low", "medium", "high", "urgent")

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[Union[date, str]] = None,
        tags: Optional[List[str]] = None,
        task_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = task_id
        self.title = title  # Validated via setter
        self.description = description.strip() if description else None
        self.category_id = category_id
        self.category_name = category_name or "Uncategorized"
        self.status = status  # Validated via setter
        self.priority = priority  # Validated via setter
        self.due_date = due_date  # Validated via setter
        self.tags = tags or []
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def title(self) -> str:
        """Task title string."""
        return self._title

    @title.setter
    def title(self, val: str) -> None:
        if not val or not val.strip():
            raise ValidationError("Task title cannot be empty.")
        clean_val = val.strip()
        if len(clean_val) > 200:
            raise ValidationError("Task title cannot exceed 200 characters.")
        self._title = clean_val

    @property
    def status(self) -> str:
        """Current lifecycle status of the task."""
        return self._status

    @status.setter
    def status(self, val: str) -> None:
        if not val:
            raise ValidationError("Status cannot be empty.")
        clean_val = val.lower().strip()
        if clean_val not in self.VALID_STATUSES:
            raise ValidationError(
                f"Invalid status '{val}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        self._status = clean_val

    @property
    def priority(self) -> str:
        """Task priority level."""
        return self._priority

    @priority.setter
    def priority(self, val: str) -> None:
        if not val:
            raise ValidationError("Priority cannot be empty.")
        clean_val = val.lower().strip()
        if clean_val not in self.VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority '{val}'. Must be one of: {', '.join(self.VALID_PRIORITIES)}"
            )
        self._priority = clean_val

    @property
    def due_date(self) -> Optional[date]:
        """Due date of the task."""
        return self._due_date

    @due_date.setter
    def due_date(self, val: Optional[Union[date, str]]) -> None:
        if val is None or val == "":
            self._due_date = None
            return

        if isinstance(val, date):
            self._due_date = val
        elif isinstance(val, str):
            try:
                self._due_date = datetime.strptime(val.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(
                    f"Invalid date format '{val}'. Please use YYYY-MM-DD."
                )
        else:
            raise ValidationError("due_date must be a date object or 'YYYY-MM-DD' string.")

    # -------------------------------------------------------------------------
    # State Transition and Domain Methods
    # -------------------------------------------------------------------------

    def mark_completed(self) -> None:
        """Transition status to completed."""
        self.status = "completed"

    def mark_in_progress(self) -> None:
        """Transition status to in_progress."""
        self.status = "in_progress"

    def mark_pending(self) -> None:
        """Transition status to pending."""
        self.status = "pending"

    def is_overdue(self) -> bool:
        """Check whether task is past its due date without completion."""
        if not self.due_date:
            return False
        return self.status != "completed" and self.due_date < date.today()

    def days_remaining(self) -> Optional[int]:
        """Return days remaining until due date, or negative if overdue."""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    def to_dict(self) -> Dict[str, Any]:
        """Convert task object to a serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue(),
            "days_remaining": self.days_remaining(),
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Task":
        """Instantiate a Task from a database query row dictionary."""
        # Parse tags from STRING_AGG or list
        raw_tags = row.get("tags")
        if isinstance(raw_tags, str):
            tags_list = [t.strip() for t in raw_tags.split(",") if t.strip()]
        elif isinstance(raw_tags, list):
            tags_list = raw_tags
        else:
            tags_list = []

        return cls(
            task_id=row.get("id"),
            title=row["title"],
            description=row.get("description"),
            category_id=row.get("category_id"),
            category_name=row.get("category_name"),
            status=row.get("status", "pending"),
            priority=row.get("priority", "medium"),
            due_date=row.get("due_date"),
            tags=tags_list,
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title='{self.title[:20]}' status='{self.status}'>"

    def __str__(self) -> str:
        status_symbol = "[X]" if self.status == "completed" else "[ ]"
        return f"{status_symbol} ({self.id}) {self.title} [Priority: {self.priority}, Category: {self.category_name}]"
