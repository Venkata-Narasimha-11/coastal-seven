"""FastAPI Product Endpoints implementing catalog search and CRUD operations."""

import math
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.deps import PaginationParams, ProductFilterParams, SessionDep
from app.crud.crud_product import crud_product
from app.crud.crud_user import crud_user
from app.schemas.common import PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalog product",
    description="Registers a new product under an existing owner. Requires a unique SKU and valid pricing.",
    responses={
        201: {"description": "Product successfully created"},
        400: {"description": "Owner does not exist or invalid pricing logic"},
        409: {"description": "Product with this SKU already exists"},
    },
)
async def create_product(
    product_in: ProductCreate,
    session: SessionDep,
) -> ProductResponse:
    """Create a new product record."""
    # Verify owner exists
    owner = await crud_user.get(session, product_in.owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Owner with ID {product_in.owner_id} does not exist.",
        )

    # Check for SKU collision
    existing_sku = await crud_product.get_by_sku(session, product_in.sku)
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_in.sku}' already exists.",
        )

    product = await crud_product.create_with_owner(session, product_in)
    return product


@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary="List and filter catalog products",
    description="Query catalog items with pagination, keyword search, price range filtering, category filtering, and availability toggles.",
)
async def list_products(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[ProductFilterParams, Depends()],
) -> PaginatedResponse[ProductResponse]:
    """Retrieve catalog products with full-text search and filters."""
    products, total = await crud_product.filter_products(
        session,
        skip=pagination.skip,
        limit=pagination.limit,
        search=filters.search,
        category=filters.category,
        min_price=filters.min_price,
        max_price=filters.max_price,
        is_available=filters.is_available,
        owner_id=filters.owner_id,
    )

    total_pages = math.ceil(total / pagination.limit) if total > 0 else 0

    return PaginatedResponse[ProductResponse](
        total=total,
        page=pagination.page,
        page_size=pagination.limit,
        total_pages=total_pages,
        items=products,
    )


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product details by ID",
    description="Retrieve full product details including the owner profile.",
    responses={
        200: {"description": "Product details with owner information"},
        404: {"description": "Product not found"},
    },
)
async def get_product_by_id(
    session: SessionDep,
    product_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the product")],
) -> ProductDetailResponse:
    """Fetch product by ID with eager loaded owner."""
    product = await crud_product.get_with_owner(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product details (Full)",
    description="Modify attributes of an existing product such as price, inventory, or description.",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found"},
        409: {"description": "SKU collision"},
    },
)
@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product details (Partial)",
    description="Partially modify attributes of an existing product such as price, inventory, or description.",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found"},
        409: {"description": "SKU collision"},
    },
)
async def update_product(
    session: SessionDep,
    product_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the product")],
    product_in: ProductUpdate,
) -> ProductResponse:
    """Update product by ID."""
    db_product = await crud_product.get(session, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )

    # Check SKU collision if updating SKU
    if product_in.sku and product_in.sku != db_product.sku:
        existing = await crud_product.get_by_sku(session, product_in.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{product_in.sku}' already exists.",
            )

    # Check discount vs price logic against existing values
    target_price = product_in.price if product_in.price is not None else db_product.price
    target_discount = (
        product_in.discount_price
        if product_in.discount_price is not None
        else db_product.discount_price
    )
    if target_discount is not None and target_discount >= target_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Discount price ({target_discount}) cannot exceed base price ({target_price}).",
        )

    updated_product = await crud_product.update(session, db_product, product_in)
    return updated_product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Permanently removes a product from the catalog.",
    responses={
        204: {"description": "Product successfully deleted"},
        404: {"description": "Product not found"},
    },
)
async def delete_product(
    session: SessionDep,
    product_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the product")],
) -> None:
    """Delete product by ID."""
    deleted = await crud_product.remove(session, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )
    return None
