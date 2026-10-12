"""ChatMessage database model for live customer-support conversations."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ChatMessage(Base):
    """Stores persistent real-time chat messages."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sender_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False, default="customer")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
