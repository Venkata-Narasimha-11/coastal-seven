"""Product CRUD Repository implementing SQLAlchemy 2.0 async queries."""

from typing import List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """Specialized CRUD operations for Product entities."""

    async def get_by_sku(self, session: AsyncSession, sku: str) -> Optional[Product]:
        """Fetch product by unique SKU."""
        stmt = select(Product).where(Product.sku == sku.strip().upper())
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_with_owner(self, session: AsyncSession, product_id: int) -> Optional[Product]:
        """Fetch product with its owner user eager loaded."""
        stmt = (
            select(Product)
            .options(selectinload(Product.owner))
            .where(Product.id == product_id)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi_by_owner(
        self,
        session: AsyncSession,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Product], int]:
        """Fetch all products owned by a specific user with pagination."""
        query = select(Product).where(Product.owner_id == owner_id)
        count_query = select(func.count()).select_from(Product).where(Product.owner_id == owner_id)

        total = await session.scalar(count_query) or 0
        paginated_query = query.offset(skip).limit(limit).order_by(Product.id.asc())
        result = await session.execute(paginated_query)
        products = list(result.scalars().all())
        return products, total

    async def filter_products(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_available: Optional[bool] = None,
        owner_id: Optional[int] = None,
    ) -> Tuple[List[Product], int]:
        """Advanced query filtering by search query, category, price range, and availability."""
        query = select(Product).options(selectinload(Product.owner))
        count_query = select(func.count()).select_from(Product)

        conditions = []

        if search:
            search_term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Product.title.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term),
                )
            )

        if category:
            conditions.append(Product.category.ilike(category.strip()))

        if min_price is not None:
            conditions.append(Product.price >= min_price)

        if max_price is not None:
            conditions.append(Product.price <= max_price)

        if is_available is not None:
            conditions.append(Product.is_available == is_available)

        if owner_id is not None:
            conditions.append(Product.owner_id == owner_id)

        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        total = await session.scalar(count_query) or 0
        paginated_query = query.offset(skip).limit(limit).order_by(Product.id.asc())
        result = await session.execute(paginated_query)
        items = list(result.scalars().all())
        return items, total

    async def create_with_owner(
        self,
        session: AsyncSession,
        obj_in: Union[ProductCreate, dict],
    ) -> Product:
        """Create a product linked to an existing owner."""
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            data = obj_in.model_dump()

        db_obj = Product(**data)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj


crud_product = CRUDProduct(Product)
