"""Category Domain Model."""

from datetime import datetime
from typing import Any, Dict, Optional

from models.exceptions import ValidationError


class Category:
    """Represents a task classification category."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        task_count: int = 0,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = category_id
        self.name = name  # Setter handles validation
        self.description = description.strip() if description else None
        self.task_count = task_count
        self.created_at = created_at

    @property
    def name(self) -> str:
        """Category name string."""
        return self._name

    @name.setter
    def name(self, val: str) -> None:
        if not val or not val.strip():
            raise ValidationError("Category name cannot be empty.")
        val_clean = val.strip()
        if len(val_clean) > 50:
            raise ValidationError("Category name cannot exceed 50 characters.")
        self._name = val_clean

    def to_dict(self) -> Dict[str, Any]:
        """Serialize category to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_count": self.task_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Category":
        """Instantiate a Category object from a database result dictionary."""
        return cls(
            category_id=row.get("id"),
            name=row["name"],
            description=row.get("description"),
            task_count=row.get("task_count", 0),
            created_at=row.get("created_at"),
        )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return f"[{self.id}] {self.name}"
