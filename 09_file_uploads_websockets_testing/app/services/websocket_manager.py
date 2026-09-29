"""WebSocket connection manager for real-time notifications and messaging.

Supports multi-client connection tracking, room/channel subscriptions,
personal directed messages, and broadcast distributions.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Set, Union

from fastapi import WebSocket

from app.schemas.websocket import (
    ConnectedClientInfo,
    WebSocketEventType,
    WebSocketMessage,
)

logger = logging.getLogger("websocket_manager")


class ConnectionManager:
    """Manages active WebSocket connections, channels, and broadcasting."""

    def __init__(self) -> None:
        # Maps client_id -> WebSocket instance
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps channel_name -> Set[client_id]
        self.channels: Dict[str, Set[str]] = {}
        # Maps client_id -> Set[channel_name]
        self.client_subscriptions: Dict[str, Set[str]] = {}

    @property
    def connection_count(self) -> int:
        """Return total number of active connections."""
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept a new WebSocket connection and track client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()

        # Join default broadcast channel
        self.subscribe(client_id, "broadcast")
        self.subscribe(client_id, "uploads")

        logger.info(
            f"Client '{client_id}' connected. Total active: {len(self.active_connections)}"
        )

        # Notify existing clients
        await self.broadcast(
            WebSocketMessage(
                event=WebSocketEventType.CLIENT_CONNECTED,
                sender_id="server",
                channel="broadcast",
                data={
                    "client_id": client_id,
                    "total_clients": len(self.active_connections),
                },
            ),
            exclude_client_id=client_id,
        )

    async def disconnect(self, client_id: str) -> None:
        """Remove a client connection and clean up subscriptions."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if client_id in self.client_subscriptions:
            for ch in list(self.client_subscriptions[client_id]):
                if ch in self.channels and client_id in self.channels[ch]:
                    self.channels[ch].remove(client_id)
            del self.client_subscriptions[client_id]

        logger.info(
            f"Client '{client_id}' disconnected. Remaining: {len(self.active_connections)}"
        )

        # Broadcast client disconnected event
        await self.broadcast(
            WebSocketMessage(
                event=WebSocketEventType.CLIENT_DISCONNECTED,
                sender_id="server",
                channel="broadcast",
                data={
                    "client_id": client_id,
                    "total_clients": len(self.active_connections),
                },
            )
        )

    def subscribe(self, client_id: str, channel: str) -> bool:
        """Subscribe client to a named channel."""
        if client_id not in self.active_connections:
            return False

        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(client_id)
        self.client_subscriptions[client_id].add(channel)
        return True

    def unsubscribe(self, client_id: str, channel: str) -> bool:
        """Unsubscribe client from a named channel."""
        if client_id in self.channels.get(channel, set()):
            self.channels[channel].remove(client_id)
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(channel)
        return True

    def _prepare_payload(self, message: Union[Dict[str, Any], WebSocketMessage]) -> str:
        """Convert a message dict or Pydantic model to JSON string."""
        if isinstance(message, WebSocketMessage):
            return message.model_dump_json()
        return json.dumps(message)

    async def send_personal_message(
        self,
        message: Union[Dict[str, Any], WebSocketMessage],
        client_id: str,
    ) -> bool:
        """Send message directly to a specific connected client."""
        websocket = self.active_connections.get(client_id)
        if not websocket:
            return False

        payload = self._prepare_payload(message)
        try:
            await websocket.send_text(payload)
            return True
        except Exception as exc:
            logger.error(f"Error sending message to client {client_id}: {exc}")
            await self.disconnect(client_id)
            return False

    async def broadcast(
        self,
        message: Union[Dict[str, Any], WebSocketMessage],
        exclude_client_id: Optional[str] = None,
    ) -> int:
        """Broadcast message to all connected clients."""
        payload = self._prepare_payload(message)
        sent_count = 0
        disconnected_clients: List[str] = []

        for cid, ws in list(self.active_connections.items()):
            if exclude_client_id and cid == exclude_client_id:
                continue
            try:
                await ws.send_text(payload)
                sent_count += 1
            except Exception as exc:
                logger.warning(f"Failed to broadcast to {cid}: {exc}")
                disconnected_clients.append(cid)

        for dead_client in disconnected_clients:
            await self.disconnect(dead_client)

        return sent_count

    async def broadcast_to_channel(
        self,
        channel: str,
        message: Union[Dict[str, Any], WebSocketMessage],
    ) -> int:
        """Broadcast message only to clients subscribed to the specified channel."""
        payload = self._prepare_payload(message)
        subscribers = list(self.channels.get(channel, set()))
        sent_count = 0
        disconnected_clients: List[str] = []

        for cid in subscribers:
            ws = self.active_connections.get(cid)
            if ws:
                try:
                    await ws.send_text(payload)
                    sent_count += 1
                except Exception:
                    disconnected_clients.append(cid)

        for dead_client in disconnected_clients:
            await self.disconnect(dead_client)

        return sent_count

    def get_clients_info(self) -> List[ConnectedClientInfo]:
        """Return information for all currently connected clients."""
        info: List[ConnectedClientInfo] = []
        for cid in self.active_connections.keys():
            subs = list(self.client_subscriptions.get(cid, set()))
            info.append(
                ConnectedClientInfo(
                    client_id=cid,
                    connected_at="active",
                    subscriptions=subs,
                )
            )
        return info


manager = ConnectionManager()
