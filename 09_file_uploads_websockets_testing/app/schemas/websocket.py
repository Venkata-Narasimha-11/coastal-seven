"""Pydantic schemas for WebSocket events, real-time notifications, and messaging."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WebSocketEventType(str, Enum):
    """Event types exchanged across WebSocket connections."""

    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"
    NOTIFICATION = "notification"
    FILE_UPLOADED = "file_uploaded"
    IMAGE_PROCESSED = "image_processed"
    CHAT_MESSAGE = "chat_message"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    SYSTEM_STATS = "system_stats"


class WebSocketMessage(BaseModel):
    """Standardized event envelope emitted to WebSocket clients."""

    event: WebSocketEventType
    sender_id: str = "server"
    channel: Optional[str] = "broadcast"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    data: Dict[str, Any] = Field(default_factory=dict)


class ClientInboundMessage(BaseModel):
    """Schema for incoming client commands via WebSocket."""

    action: str = Field(
        ...,
        description="Action to execute: 'ping', 'broadcast', 'direct_message', 'subscribe', 'unsubscribe'",
    )
    target_id: Optional[str] = Field(
        default=None,
        description="Target client ID for direct messages",
    )
    channel: Optional[str] = Field(
        default=None,
        description="Channel topic for subscription",
    )
    message: Optional[str] = Field(
        default=None,
        description="Text payload or payload message",
    )
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional structured metadata",
    )


class ConnectedClientInfo(BaseModel):
    """Metadata regarding an active connected client."""

    client_id: str
    connected_at: str
    subscriptions: List[str]
