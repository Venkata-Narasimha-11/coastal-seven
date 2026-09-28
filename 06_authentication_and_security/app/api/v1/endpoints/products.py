"""Secure Product Endpoints demonstrating Role-Based Access Control (RBAC).

Practice Requirements:
- Authenticate and authorize product catalog operations.
- Only administrators ('admin' role) can CREATE, EDIT (PUT/PATCH), or DELETE products.
- Standard users ('user' role) can browse and view product details.
- Unauthenticated requests are rejected with 401 Unauthorized.
- Unauthorized roles attempting write operations are rejected with 403 Forbidden.
"""

import math
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.api.deps import (
    CurrentAdminUserDep,
    CurrentUserDep,
    PaginationParams,
    ProductFilterParams,
    SessionDep,
)
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


# ------------------------------------------------------------------------------
# 9. PRACTICE – SECURE PRODUCT API (RBAC IMPLEMENTATION)
# ------------------------------------------------------------------------------

@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary="List catalog products (Authenticated)",
    description="Query catalog items with pagination and filters. Accessible to all authenticated users.",
    responses={
        200: {"description": "Paginated list of products"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
    },
)
async def list_products(
    session: SessionDep,
    current_user: CurrentUserDep,
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
    summary="Get product details (Authenticated)",
    description="Retrieve product details including owner information. Accessible to all authenticated users.",
    responses={
        200: {"description": "Product details with owner summary"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
        404: {"description": "Product not found"},
    },
)
async def get_product_by_id(
    session: SessionDep,
    current_user: CurrentUserDep,
    product_id: Annotated[int, Path(..., ge=1, description="Product ID")],
) -> ProductDetailResponse:
    """Fetch product by ID with eager loaded owner."""
    product = await crud_product.get_with_owner(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )
    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product (Admin Only)",
    description="Registers a new catalog product. Strictly restricted to administrators with role 'admin'.",
    responses={
        201: {"description": "Product created successfully"},
        400: {"description": "Owner does not exist or validation error"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
        403: {"description": "Forbidden - Insufficient privileges (Admin role required)"},
        409: {"description": "Product with this SKU already exists"},
    },
)
async def create_product(
    product_in: ProductCreate,
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
) -> ProductResponse:
    """Create a new product record (Admin only)."""
    # Default owner to the authenticated admin if not specified
    target_owner_id = product_in.owner_id or admin_user.id

    # Verify owner exists
    owner = await crud_user.get(session, target_owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Owner with ID {target_owner_id} does not exist.",
        )

    # Check for SKU uniqueness
    existing_sku = await crud_product.get_by_sku(session, product_in.sku)
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_in.sku}' already exists.",
        )

    data = product_in.model_dump()
    data["owner_id"] = target_owner_id
    product = await crud_product.create_with_owner(session, data)
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Full update product details (Admin Only)",
    description="Modifies all fields of an existing product. Strictly restricted to administrators.",
    responses={
        200: {"description": "Product updated successfully"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
        403: {"description": "Forbidden - Admin role required"},
        404: {"description": "Product not found"},
        409: {"description": "SKU collision"},
    },
)
async def update_product_put(
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
    product_id: Annotated[int, Path(..., ge=1, description="Product ID")],
    product_in: ProductUpdate,
) -> ProductResponse:
    """Full update product by ID (Admin only)."""
    db_product = await crud_product.get(session, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )

    if product_in.sku and product_in.sku != db_product.sku:
        existing = await crud_product.get_by_sku(session, product_in.sku)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{product_in.sku}' already exists.",
            )

    updated = await crud_product.update(session, db_obj=db_product, obj_in=product_in)
    return updated


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Partial update product details (Admin Only)",
    description="Partially modifies attributes of an existing product. Strictly restricted to administrators.",
    responses={
        200: {"description": "Product updated successfully"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
        403: {"description": "Forbidden - Admin role required"},
        404: {"description": "Product not found"},
        409: {"description": "SKU collision"},
    },
)
async def update_product_patch(
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
    product_id: Annotated[int, Path(..., ge=1, description="Product ID")],
    product_in: ProductUpdate,
) -> ProductResponse:
    """Partial update product by ID (Admin only)."""
    db_product = await crud_product.get(session, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )

    if product_in.sku and product_in.sku != db_product.sku:
        existing = await crud_product.get_by_sku(session, product_in.sku)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{product_in.sku}' already exists.",
            )

    updated = await crud_product.update(session, db_obj=db_product, obj_in=product_in)
    return updated


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product (Admin Only)",
    description="Deletes a product from the catalog. Strictly restricted to administrators.",
    responses={
        204: {"description": "Product deleted successfully"},
        401: {"description": "Unauthorized - Missing or invalid Bearer token"},
        403: {"description": "Forbidden - Admin role required"},
        404: {"description": "Product not found"},
    },
)
async def delete_product(
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
    product_id: Annotated[int, Path(..., ge=1, description="Product ID")],
) -> Response:
    """Delete product by ID (Admin only)."""
    db_product = await crud_product.get(session, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found.",
        )

    await crud_product.remove(session, id=product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
