"""CRUD repositories aggregating database operations."""
from app.crud.base import CRUDBase
from app.crud.crud_project import project_crud
from app.crud.crud_task import task_crud
from app.crud.crud_user import user_crud

__all__ = [
    "CRUDBase",
    "user_crud",
    "project_crud",
    "task_crud",
]
