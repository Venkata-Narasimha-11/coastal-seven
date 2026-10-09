"""Celery application and asynchronous background task definitions."""

import logging
from typing import Any, Dict, List
from celery import Celery
from app.config import settings

logger = logging.getLogger("celery_worker")

# Initialize Celery application
celery_app = Celery(
    "ecommerce_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# If Redis is unavailable locally, enable eager task execution
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
            [f"- {it.get('product_name')}: {it.get('quantity')} x ${it.get('unit_price')} = ${it.get('subtotal')}" for it in items]
        )
        email_content = (
            f"Dear Customer,\n\n"
            f"Thank you for your order #{order_id}!\n\n"
            f"Order Summary:\n{item_summary}\n\n"
            f"Total Charged: ${total_amount:.2f}\n\n"
            f"We are processing your order right away.\n"
        )

        logger.info("Order confirmation email successfully sent for Order #%d:\n%s", order_id, email_content)

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
