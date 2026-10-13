"""Celery application and asynchronous background task definitions."""

import csv
import logging
import time
from pathlib import Path
from typing import Any, Dict, List
from celery import Celery

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.config import settings
from app.database import SessionLocal
from app.models.order import Order
from app.models.product import Product

logger = logging.getLogger("celery_worker")

# -------------------------------------------------------------
# 1. Initialize Celery Application
# -------------------------------------------------------------
celery_app = Celery(
    "ecommerce_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Redis local ga lekapothe fallback (eager mode)
from app.services.redis_service import redis_client
import fakeredis

is_fake_redis = isinstance(redis_client, fakeredis.FakeRedis)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_always_eager=is_fake_redis,
    task_eager_propagates=True,
)

if is_fake_redis:
    celery_app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_store_eager_result=True,
    )


# -------------------------------------------------------------
# 2. Existing Task: Order Confirmation Email
# -------------------------------------------------------------
@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_order_confirmation_email(
    self,
    order_id: int,
    user_email: str,
    total_amount: float,
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Background task to send an itemized order confirmation receipt to the customer."""
    try:
        logger.info(
            "Dispatching order confirmation email for Order #%s to %s",
            order_id,
            user_email,
        )

        item_summary = "\n".join(
            [
                f"- {it.get('product_name')}: {it.get('quantity')} x ${it.get('unit_price')} = ${it.get('subtotal')}"
                for it in items
            ]
        )
        email_content = (
            f"Dear Customer,\n\n"
            f"Thank you for your order #{order_id}!\n\n"
            f"Order Summary:\n{item_summary}\n\n"
            f"Total Charged: ${total_amount:.2f}\n\n"
            f"We are processing your order right away.\n"
        )

        logger.info(
            "Order confirmation email successfully sent for Order #%d:\n%s",
            order_id,
            email_content,
        )

        return {
            "status": "SENT",
            "order_id": order_id,
            "recipient": user_email,
            "items_count": len(items),
            "total_amount": total_amount,
        }
    except Exception as exc:
        logger.error("Failed to send order confirmation email: %s. Retrying...", exc)
        raise self.retry(exc=exc)


# -------------------------------------------------------------
# 3. DAY 18 NEW TASK: PDF Invoice Generation with Live Progress
# -------------------------------------------------------------
@celery_app.task(bind=True)
def generate_pdf_invoice_task(self, order_id: int) -> Dict[str, Any]:
    """
    Background Task: Generates an Amazon-style PDF Tax Invoice with Company Stamp & QR Code.
    Periodically updates task state with progress (0% -> 100%) for React UI tracking.
    """
    from sqlalchemy.orm import selectinload, joinedload
    from app.models.order import OrderItem
    from app.services.invoice_generator import generate_enterprise_invoice_pdf

    # Step 1: Starting & fetching data (20%)
    self.update_state(
        state="PROGRESS",
        meta={"progress": 20, "message": "Fetching order & customer details from database..."},
    )
    time.sleep(0.8)

    db = SessionLocal()
    try:
        # Eager load items, products, and user to avoid N+1 queries
        order = (
            db.query(Order)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.user),
            )
            .filter(Order.id == order_id)
            .first()
        )
        if not order:
            raise ValueError(f"Order #{order_id} not found in database")

        # Step 2: Creating Enterprise PDF Layout & Stamp (55%)
        self.update_state(
            state="PROGRESS",
            meta={"progress": 55, "message": "Applying SIVORA official stamp & calculating taxes..."},
        )
        time.sleep(1.0)

        invoices_dir = settings.UPLOAD_DIR / "invoices"
        invoices_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"invoice_order_{order_id}.pdf"
        pdf_path = invoices_dir / pdf_filename

        # Render Enterprise Amazon-Style Invoice
        generate_enterprise_invoice_pdf(order, pdf_path)

        # Step 3: Finalizing (90%)
        self.update_state(
            state="PROGRESS",
            meta={"progress": 90, "message": "Embedding digital QR code & saving PDF..."},
        )
        time.sleep(0.5)

        # Step 4: Complete
        return {
            "order_id": order_id,
            "file_url": f"/uploads/invoices/{pdf_filename}",
            "message": "Enterprise Tax Invoice generated successfully with Official Stamp!",
        }
    finally:
        db.close()


# -------------------------------------------------------------
# 4. DAY 18 NEW TASK: Bulk CSV Import with Live Progress Bar
# -------------------------------------------------------------
@celery_app.task(bind=True)
def bulk_import_products_csv_task(self, file_path_str: str) -> Dict[str, Any]:
    """
    Background Task: Reads products from uploaded CSV file in batches,
    inserts into database, and updates progress percentage for the UI progress bar.
    """
    file_path = Path(file_path_str)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path_str}")

    db = SessionLocal()
    try:
        # Step A: Total lines calculate cheyali
        with open(file_path, "r", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1

        if total_rows <= 0:
            return {"imported_count": 0, "message": "Empty CSV file"}

        imported_count = 0

        # Step B: Read & Insert each product
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for index, row in enumerate(reader, start=1):
                base_name = row.get("name", f"Imported Product {index}")
                slug = row.get("slug") or f"{base_name.lower().replace(' ', '-')}-{int(time.time())}-{index}"
                
                raw_img = row.get("image_url") or row.get("thumbnail_url")
                if not raw_img:
                    name_l = base_name.lower()
                    if "headphone" in name_l or "audio" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"
                    elif "monitor" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80"
                    elif "mouse" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80"
                    elif "keyboard" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80"
                    elif "phone" in name_l or "iphone" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80"
                    elif "laptop" in name_l or "macbook" in name_l:
                        raw_img = "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80"
                    else:
                        raw_img = "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=80"

                product = Product(
                    name=base_name,
                    slug=slug,
                    description=row.get("description", "Bulk imported product"),
                    price=float(row.get("price", 10.0)),
                    stock=int(row.get("stock", 50)),
                    category_id=int(row.get("category_id", 1)),
                    image_url=raw_img,
                    thumbnail_url=raw_img,
                    is_active=True,
                )
                db.add(product)
                imported_count += 1
                db.commit()

                # Progress percentage calculate chestunnam (0 to 100%)
                current_percent = int((index / total_rows) * 100)

                # Celery status update: UI lo progress bar animate avvadaniki!
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "progress": current_percent,
                        "processed": index,
                        "total": total_rows,
                        "message": f"Importing product {index} of {total_rows}...",
                    },
                )
                time.sleep(0.05)

        # Invalidate product caches so Admin & Storefront show fresh products immediately
        from app.services.redis_service import CacheService
        CacheService.invalidate_product_caches()

        return {
            "imported_count": imported_count,
            "message": f"Successfully imported {imported_count} products!",
        }
    finally:
        db.close()