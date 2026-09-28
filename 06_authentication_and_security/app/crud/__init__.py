"""Export CRUD repositories."""

from app.crud.crud_product import crud_product
from app.crud.crud_user import crud_user

__all__ = ["crud_user", "crud_product"]
