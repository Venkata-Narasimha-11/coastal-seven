"""CRUD repository layer package exposing singleton repositories."""

from app.crud.base import CRUDBase
from app.crud.crud_user import CRUDUser, crud_user
from app.crud.crud_product import CRUDProduct, crud_product

__all__ = ["CRUDBase", "CRUDUser", "crud_user", "CRUDProduct", "crud_product"]
