"""Product catalog, category management, image processing, and Redis caching endpoints."""

import os
import re
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from PIL import Image
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.redis_service import CacheService
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/products", tags=["Products & Categories"])


def slugify(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


# ---------------------------------------------------------
# Category Endpoints
# ---------------------------------------------------------

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all available product categories."""
    cache_key = "categories:all"
    cached = CacheService.get(cache_key)
    if cached:
        return cached

    categories = db.query(Category).order_by(Category.name.asc()).all()
    # Serialize for cache
    serialized = [CategoryResponse.model_validate(c).model_dump() for c in categories]
    CacheService.set(cache_key, serialized, ttl_seconds=600)
    return categories


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new category (Admin only)."""
    slug = slugify(category_in.name)
    existing = db.query(Category).filter(or_(Category.name == category_in.name, Category.slug == slug)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name or slug already exists",
        )

    category = Category(
        name=category_in.name,
        slug=slug,
        description=category_in.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    CacheService.invalidate_pattern("categories:*")
    return category


# ---------------------------------------------------------
# Product Endpoints
# ---------------------------------------------------------

@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="price_asc, price_desc, newest, name_asc"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """List products with pagination, category filter, search, price range filter, sorting, and Redis caching."""
    cache_key = f"products:list:{category_id}:{search}:{sort_by}:{min_price}:{max_price}:{page}:{size}"
    cached = CacheService.get(cache_key)
    if cached:
        return cached

    query = db.query(Product).filter(Product.is_active == True)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(Product.name.ilike(search_filter), Product.description.ilike(search_filter))
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    else:  # default or "newest"
        query = query.order_by(Product.created_at.desc())

    total = query.count()
    offset = (page - 1) * size
    products = query.offset(offset).limit(size).all()

    response_data = {
        "items": [ProductResponse.model_validate(p).model_dump() for p in products],
        "total": total,
        "page": page,
        "size": size,
    }

    CacheService.set(cache_key, response_data, ttl_seconds=settings.REDIS_CACHE_TTL_SECONDS)
    return response_data


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed product information by ID with Redis caching."""
    cache_key = f"product:detail:{product_id}"
    cached = CacheService.get(cache_key)
    if cached:
        return cached

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    validated = ProductResponse.model_validate(product).model_dump()
    CacheService.set(cache_key, validated, ttl_seconds=settings.REDIS_CACHE_TTL_SECONDS)
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new product catalog item (Admin only)."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == product_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category does not exist",
        )

    slug_base = slugify(product_in.name)
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"

    product = Product(
        name=product_in.name,
        slug=slug,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        category_id=product_in.category_id,
        image_url=product_in.image_url,
        thumbnail_url=product_in.thumbnail_url,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    CacheService.invalidate_product_caches()
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update product information and invalidate cache (Admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    if "category_id" in update_data and update_data["category_id"] is not None:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    CacheService.invalidate_product_caches(product_id)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Deactivate or remove a product (Admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()

    CacheService.invalidate_product_caches(product_id)
    return None


@router.post("/{product_id}/upload-image", response_model=ProductResponse)
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Upload product image, auto-generate thumbnail, and update product record."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed: JPEG, PNG, WebP",
        )

    upload_folder = settings.UPLOAD_DIR
    upload_folder.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    unique_name = f"prod_{product_id}_{uuid.uuid4().hex[:8]}"
    main_file_path = upload_folder / f"{unique_name}{ext}"
    thumb_file_path = upload_folder / f"{unique_name}_thumb.webp"

    # Save original image
    with open(main_file_path, "wb") as f:
        f.write(file.file.read())

    # Generate thumbnail using Pillow
    try:
        with Image.open(main_file_path) as img:
            img.thumbnail((200, 200))
            img.save(thumb_file_path, "WEBP", quality=85)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image thumbnail generation failed: {str(e)}",
        )

    product.image_url = f"/uploads/{main_file_path.name}"
    product.thumbnail_url = f"/uploads/{thumb_file_path.name}"
    db.commit()
    db.refresh(product)

    CacheService.invalidate_product_caches(product_id)
    return product
