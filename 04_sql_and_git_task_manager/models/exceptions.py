"""Custom domain exceptions for CLI Task Manager."""


class TaskManagerError(Exception):
    """Base exception for all domain-specific Task Manager errors."""
    pass


class ValidationError(TaskManagerError):
    """Raised when task or category data violates domain constraints."""
    pass


class TaskNotFoundError(TaskManagerError):
    """Raised when an operation references a non-existent task ID."""
    pass


class CategoryNotFoundError(TaskManagerError):
    """Raised when an operation references a non-existent category ID or name."""
    pass


class DatabaseError(TaskManagerError):
    """Raised when an underlying database execution fails."""
    pass
