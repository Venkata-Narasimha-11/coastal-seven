"""WebSocket ConnectionManager and real-time order tracking endpoint."""

import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("websocket_manager")
router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    """Manages active WebSocket connections grouped by order_id rooms and admin channel."""

    def __init__(self):
        # order_id -> list of active WebSocket client connections
        self.active_rooms: Dict[int, List[WebSocket]] = {}
        # Active admin dashboard connections for live sales & inventory alerts
        self.admin_connections: List[WebSocket] = []
        # room_id -> list of active WebSocket client connections for live chat
        self.chat_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, order_id: int, websocket: WebSocket):
        """Accept connection and register into order-specific room."""
        await websocket.accept()
        if order_id not in self.active_rooms:
            self.active_rooms[order_id] = []
        self.active_rooms[order_id].append(websocket)
        logger.info("WebSocket client connected to order room %d", order_id)

    def disconnect(self, order_id: int, websocket: WebSocket):
        """Remove connection upon disconnection."""
        if order_id in self.active_rooms:
            if websocket in self.active_rooms[order_id]:
                self.active_rooms[order_id].remove(websocket)
            if not self.active_rooms[order_id]:
                del self.active_rooms[order_id]
        logger.info("WebSocket client disconnected from order room %d", order_id)

    async def broadcast_order_update(self, order_id: int, message: dict):
        """Broadcast live order update payload to all clients tracking order_id."""
        if order_id in self.active_rooms:
            dead_connections = []
            for connection in self.active_rooms[order_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning("Failed to send message to WS client: %s", e)
                    dead_connections.append(connection)

            for dead in dead_connections:
                self.disconnect(order_id, dead)

    async def connect_admin(self, websocket: WebSocket):
        """Accept connection from Admin dashboard."""
        await websocket.accept()
        self.admin_connections.append(websocket)
        logger.info("Admin WebSocket connected. Total admins: %d", len(self.admin_connections))

    def disconnect_admin(self, websocket: WebSocket):
        """Remove admin connection."""
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
        logger.info("Admin WebSocket disconnected. Remaining: %d", len(self.admin_connections))

    async def connect_chat(self, room_id: str, websocket: WebSocket):
        """Accept connection and register into specific chat room."""
        await websocket.accept()
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = []
        self.chat_rooms[room_id].append(websocket)
        logger.info("WebSocket client connected to chat room %s", room_id)

    def disconnect_chat(self, room_id: str, websocket: WebSocket):
        """Remove connection upon chat disconnection."""
        if room_id in self.chat_rooms:
            if websocket in self.chat_rooms[room_id]:
                self.chat_rooms[room_id].remove(websocket)
            if not self.chat_rooms[room_id]:
                del self.chat_rooms[room_id]
        logger.info("WebSocket client disconnected from chat room %s", room_id)

    async def broadcast_chat(self, room_id: str, message: dict):
        """Broadcast live chat message to all connected clients in the room."""
        if room_id in self.chat_rooms:
            dead_conns = []
            for ws in self.chat_rooms[room_id]:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.warning("Failed to send chat message to WS: %s", e)
                    dead_conns.append(ws)
            for dead in dead_conns:
                self.disconnect_chat(room_id, dead)

    async def broadcast_admin_event(self, message: dict):
        """Broadcast instant sales, new orders, and out-of-stock alerts to all connected admins."""
        dead_conns = []
        for ws in self.admin_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning("Failed to send message to Admin WS: %s", e)
                dead_conns.append(ws)
        for dead in dead_conns:
            self.disconnect_admin(dead)


manager = ConnectionManager()


@router.websocket("/ws/orders/{order_id}")
async def order_status_websocket(websocket: WebSocket, order_id: int):
    """Full-duplex WebSocket endpoint for receiving live order status updates."""
    await manager.connect(order_id, websocket)
    try:
        # Send initial confirmation message
        await websocket.send_json({
            "event": "CONNECTED",
            "order_id": order_id,
            "message": f"Connected to live updates for Order #{order_id}",
        })
        while True:
            # Keep connection open and listen for client pings/messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
    except Exception as e:
        logger.error("WebSocket unexpected error on order %d: %s", order_id, e)
        manager.disconnect(order_id, websocket)


@router.websocket("/ws/admin")
async def admin_live_alerts_websocket(websocket: WebSocket):
    """Full-duplex WebSocket endpoint for Admin to receive instant order and out-of-stock alerts."""
    await manager.connect_admin(websocket)
    try:
        await websocket.send_json({
            "event": "ADMIN_CONNECTED",
            "message": "Connected to real-time Admin Sales & Inventory Alerts channel",
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_admin(websocket)
    except Exception as e:
        logger.error("Admin WebSocket unexpected error: %s", e)
        manager.disconnect_admin(websocket)


@router.websocket("/ws/chat/{room_id}")
async def live_chat_websocket(websocket: WebSocket, room_id: str):
    """Full-duplex WebSocket endpoint for real-time customer <-> admin support chat."""
    await manager.connect_chat(room_id, websocket)
    try:
        # Acknowledge connection
        await websocket.send_json({
            "event": "CHAT_JOINED",
            "room_id": room_id,
            "message": f"Connected to live chat room #{room_id}",
        })
        while True:
            # Receive message payload from client
            payload = await websocket.receive_json()
            # Broadcast to all participants in this room
            await manager.broadcast_chat(room_id, payload)
    except WebSocketDisconnect:
        manager.disconnect_chat(room_id, websocket)
    except Exception as e:
        logger.error("Live chat WS error on room %s: %s", room_id, e)
        manager.disconnect_chat(room_id, websocket)


