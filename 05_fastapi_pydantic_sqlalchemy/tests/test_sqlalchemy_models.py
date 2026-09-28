"""Unit tests for SQLAlchemy 2.0 DeclarativeBase, relationships, and cascades."""

import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.models.product import Product


@pytest.mark.asyncio
class TestSQLAlchemy2Models:
    """Test suite for SQLAlchemy 2.0 ORM features."""

    async def test_create_user_and_product_relationship(self, db_session: AsyncSession):
        """Verify User and Product 1-to-many and many-to-1 relationship mapping."""
        uid = uuid.uuid4().hex[:8]
        # 1. Create a test owner
        user = User(
            username=f"orm_{uid}",
            email=f"orm_{uid}@test.com",
            hashed_password=hash_password("OrmPassword123!"),
            full_name="ORM Tester",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None

        # 2. Create products linked to the user
        prod1 = Product(
            title="ORM Test Keyboard",
            sku=f"KB-{uid}",
            price=80.00,
            category="Electronics",
            owner=user,
        )
        prod2 = Product(
            title="ORM Test Mouse",
            sku=f"MS-{uid}",
            price=40.00,
            category="Electronics",
            owner=user,
        )
        db_session.add_all([prod1, prod2])
        await db_session.commit()

        # 3. Query user with selectinload for products
        stmt = (
            select(User)
            .options(selectinload(User.products))
            .where(User.id == user.id)
        )
        result = await db_session.execute(stmt)
        fetched_user = result.scalars().first()

        assert fetched_user is not None
        assert len(fetched_user.products) == 2
        skus = [p.sku for p in fetched_user.products]
        assert f"KB-{uid}" in skus
        assert f"MS-{uid}" in skus

        # 4. Check back_populates owner on product
        prod_stmt = (
            select(Product)
            .options(selectinload(Product.owner))
            .where(Product.id == prod1.id)
        )
        prod_result = await db_session.execute(prod_stmt)
        fetched_prod = prod_result.scalars().first()
        assert fetched_prod.owner.username == f"orm_{uid}"

    async def test_cascade_delete_orphans(self, db_session: AsyncSession):
        """Verify cascade='all, delete-orphan' removes linked products on user deletion."""
        uid = uuid.uuid4().hex[:8]
        # 1. Create temporary user
        user = User(
            username=f"cas_{uid}",
            email=f"cas_{uid}@test.com",
            hashed_password=hash_password("CascadePass123!"),
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # 2. Add product
        prod = Product(
            title="Cascade Monitor",
            sku=f"MN-{uid}",
            price=299.99,
            category="Electronics",
            owner_id=user.id,
        )
        db_session.add(prod)
        await db_session.flush()
        prod_id = prod.id

        # 3. Delete user
        await db_session.delete(user)
        await db_session.flush()

        # 4. Product should be deleted automatically by database foreign key CASCADE
        check_stmt = select(Product).where(Product.id == prod_id)
        check_res = await db_session.execute(check_stmt)
        assert check_res.scalars().first() is None
