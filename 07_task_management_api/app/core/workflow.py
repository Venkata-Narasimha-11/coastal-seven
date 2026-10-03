"""Task Status Workflow State Machine and Transition Engine."""

from enum import Enum
from typing import Dict, List, Optional, Set
from app.core.exceptions import InvalidWorkflowTransitionError, PermissionDeniedError


class TaskStatus(str, Enum):
    """Enumeration of possible task lifecycle statuses."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Enumeration of task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Valid state transitions lookup table
# Source status -> Allowed target statuses
WORKFLOW_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
    TaskStatus.TODO: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED,
    },
    TaskStatus.IN_PROGRESS: {
        TaskStatus.REVIEW,
        TaskStatus.TODO,
        TaskStatus.CANCELLED,
    },
    TaskStatus.REVIEW: {
        TaskStatus.COMPLETED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED,
    },
    TaskStatus.COMPLETED: {
        TaskStatus.IN_PROGRESS,  # Reopen requires MANAGER or ADMIN
    },
    TaskStatus.CANCELLED: {
        TaskStatus.TODO,         # Reopen requires MANAGER or ADMIN
    },
}

# Terminal states requiring privileged roles (Manager/Admin) to reopen
REOPEN_TRANSITIONS = {
    (TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS),
    (TaskStatus.CANCELLED, TaskStatus.TODO),
}

# Approval transitions that require review approval
APPROVAL_TRANSITIONS = {
    (TaskStatus.REVIEW, TaskStatus.COMPLETED),
}


class WorkflowEngine:
    """Validates and governs task status transitions according to business rules and RBAC."""

    @staticmethod
    def get_allowed_transitions(current_status: TaskStatus) -> List[str]:
        """Return list of valid next status values for a given status."""
        return [s.value for s in WORKFLOW_TRANSITIONS.get(current_status, set())]

    @classmethod
    def validate_transition(
        cls,
        current_status: TaskStatus,
        target_status: TaskStatus,
        user_role: str,
        is_task_assignee: bool = False,
        is_task_creator: bool = False,
        is_project_owner: bool = False,
    ) -> None:
        """
        Validate whether a transition from current_status to target_status is permitted,
        both by the workflow graph and by the user's role/permissions.
        """
        if current_status == target_status:
            return  # No-op status change

        # 1. Viewers cannot modify status (RBAC check takes precedence)
        if user_role == "viewer":
            raise PermissionDeniedError("Viewers have read-only access and cannot change task status.")

        allowed = WORKFLOW_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise InvalidWorkflowTransitionError(
                current_status=current_status.value,
                target_status=target_status.value,
                allowed_transitions=[s.value for s in allowed],
            )

        # Check role permissions for special transitions
        is_privileged = user_role in {"admin", "manager"} or is_project_owner

        # 2. Reopening completed or cancelled tasks requires Manager/Admin or Project Owner
        if (current_status, target_status) in REOPEN_TRANSITIONS:
            if not is_privileged:
                raise PermissionDeniedError(
                    f"Only Project Managers, Admins, or Project Owners can reopen {current_status.value} tasks."
                )

        # 3. For developers/members, they must be the assignee, creator, or project owner
        if user_role in {"developer", "member"}:
            if not (is_task_assignee or is_task_creator or is_project_owner):
                raise PermissionDeniedError(
                    "You can only update status for tasks that are assigned to you or created by you."
                )
