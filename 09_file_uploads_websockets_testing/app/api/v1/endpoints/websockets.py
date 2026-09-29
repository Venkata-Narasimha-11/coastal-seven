"""WebSocket endpoints and connection routes for real-time messaging."""

import json
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel, Field

from app.api.deps import get_connection_manager
from app.schemas.websocket import (
    ConnectedClientInfo,
    WebSocketEventType,
    WebSocketMessage,
)
from app.services.websocket_manager import ConnectionManager

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class BroadcastRequest(BaseModel):
    """Payload for HTTP triggered broadcast."""

    message: str = Field(..., description="Message string to broadcast")
    channel: str = Field(default="broadcast", description="Target channel or broadcast")
    data: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload")


async def _handle_direct_message(
    manager: ConnectionManager, client_id: str, data: Dict[str, Any]
) -> None:
    """Send a direct message from one client to another."""
    target_id = data.get("target_id")
    msg_body = data.get("message", "")
    if not target_id:
        return

    sent = await manager.send_personal_message(
        WebSocketMessage(
            event=WebSocketEventType.CHAT_MESSAGE,
            sender_id=client_id,
            channel="direct",
            data={"message": msg_body, "from": client_id},
        ),
        target_id,
    )
    if not sent:
        await manager.send_personal_message(
            WebSocketMessage(
                event=WebSocketEventType.ERROR,
                sender_id="server",
                data={"error": f"Target client '{target_id}' is offline."},
            ),
            client_id,
        )


async def _handle_chat_or_broadcast(
    manager: ConnectionManager, client_id: str, data: Dict[str, Any]
) -> None:
    """Broadcast chat message to specific channel or globally."""
    msg_body = data.get("message", "")
    channel = data.get("channel", "broadcast")
    msg = WebSocketMessage(
        event=WebSocketEventType.CHAT_MESSAGE,
        sender_id=client_id,
        channel=channel,
        data={"message": msg_body, "sender": client_id},
    )
    if channel == "broadcast":
        await manager.broadcast(msg)
    else:
        await manager.broadcast_to_channel(channel, msg)


async def _process_incoming_action(
    action: str, data: Dict[str, Any], client_id: str, manager: ConnectionManager
) -> None:
    """Dispatch client WebSocket commands."""
    if action == "ping":
        await manager.send_personal_message(
            WebSocketMessage(
                event=WebSocketEventType.HEARTBEAT,
                sender_id="server",
                data={"reply": "pong"},
            ),
            client_id,
        )
    elif action == "subscribe":
        channel = data.get("channel", "broadcast")
        manager.subscribe(client_id, channel)
        await manager.send_personal_message(
            WebSocketMessage(
                event=WebSocketEventType.NOTIFICATION,
                sender_id="server",
                data={"message": f"Subscribed to channel: {channel}"},
            ),
            client_id,
        )
    elif action == "unsubscribe":
        channel = data.get("channel", "broadcast")
        manager.unsubscribe(client_id, channel)
        await manager.send_personal_message(
            WebSocketMessage(
                event=WebSocketEventType.NOTIFICATION,
                sender_id="server",
                data={"message": f"Unsubscribed from channel: {channel}"},
            ),
            client_id,
        )
    elif action == "direct_message":
        await _handle_direct_message(manager, client_id, data)
    elif action in ("broadcast", "chat"):
        await _handle_chat_or_broadcast(manager, client_id, data)


@router.websocket("/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
) -> None:
    """Primary WebSocket endpoint for real-time bidirectional communication."""
    await manager.connect(websocket, client_id)

    # Send welcome / connection acknowledged event
    await manager.send_personal_message(
        WebSocketMessage(
            event=WebSocketEventType.NOTIFICATION,
            sender_id="server",
            channel="broadcast",
            data={
                "message": f"Welcome, client '{client_id}'! You are connected to the Real-Time Hub.",
                "client_id": client_id,
            },
        ),
        client_id,
    )

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
            except Exception:
                data = {"action": "chat", "message": raw_text}

            action = data.get("action", "chat")
            await _process_incoming_action(action, data, client_id, manager)

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception:
        await manager.disconnect(client_id)


@router.websocket("/channel/{channel_name}/{client_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket,
    channel_name: str,
    client_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
) -> None:
    """Dedicated topic/channel WebSocket endpoint."""
    await manager.connect(websocket, client_id)
    manager.subscribe(client_id, channel_name)

    await manager.send_personal_message(
        WebSocketMessage(
            event=WebSocketEventType.NOTIFICATION,
            sender_id="server",
            channel=channel_name,
            data={"message": f"Connected to dedicated channel '{channel_name}'."},
        ),
        client_id,
    )

    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast_to_channel(
                channel_name,
                WebSocketMessage(
                    event=WebSocketEventType.CHAT_MESSAGE,
                    sender_id=client_id,
                    channel=channel_name,
                    data={"message": text, "channel": channel_name},
                ),
            )
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception:
        await manager.disconnect(client_id)


@router.post(
    "/broadcast",
    status_code=status.HTTP_200_OK,
    summary="Broadcast a message via HTTP to all active WebSocket clients",
)
async def http_broadcast(
    payload: BroadcastRequest,
    manager: ConnectionManager = Depends(get_connection_manager),
) -> Dict[str, Any]:
    """Allows REST clients / background tasks to broadcast notifications to WebSocket listeners."""
    msg = WebSocketMessage(
        event=WebSocketEventType.NOTIFICATION,
        sender_id="http_api",
        channel=payload.channel,
        data={"message": payload.message, **payload.data},
    )

    if payload.channel == "broadcast":
        sent = await manager.broadcast(msg)
    else:
        sent = await manager.broadcast_to_channel(payload.channel, msg)

    return {
        "success": True,
        "recipients_reached": sent,
        "channel": payload.channel,
        "message": payload.message,
    }


@router.get(
    "/clients",
    response_model=List[ConnectedClientInfo],
    summary="List all currently connected WebSocket clients",
)
def get_connected_clients(
    manager: ConnectionManager = Depends(get_connection_manager),
) -> List[ConnectedClientInfo]:
    """Retrieve metadata of all currently connected WebSocket clients."""
    return manager.get_clients_info()
