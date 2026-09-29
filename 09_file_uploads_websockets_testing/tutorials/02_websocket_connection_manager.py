"""Tutorial 2: WebSockets & ConnectionManager Deep Dive.

Topics covered:
1. WebSocket Protocol Fundamentals (RFC 6455): HTTP Handshake -> TCP Full Duplex.
2. ConnectionManager Design Pattern: Tracking active connections in memory.
3. Message Distribution Patterns:
   - Personal Direct Messaging
   - Topic / Channel Subscriptions
   - System-wide Broadcasting
4. Disconnect Handling & Resource Cleanup.
5. Heartbeat / Keepalive mechanisms.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure module importability
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.websocket import WebSocketEventType, WebSocketMessage
from app.services.websocket_manager import ConnectionManager


class MockWebSocket:
    """Simulated WebSocket for pedagogical demonstration without network overhead."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self.inbox: List[str] = []
        self.accepted = False

    async def accept(self) -> None:
        self.accepted = True

    async def send_text(self, text: str) -> None:
        self.inbox.append(text)


async def run_websocket_simulation() -> None:
    print("=" * 70)
    print("WEBSOCKET CONNECTION MANAGER & MULTI-CLIENT SIMULATION")
    print("=" * 70)

    manager = ConnectionManager()

    # 1. Connect three mock clients
    ws_alice = MockWebSocket("Alice")
    ws_bob = MockWebSocket("Bob")
    ws_charlie = MockWebSocket("Charlie")

    print("[*] Connecting Alice, Bob, and Charlie...")
    await manager.connect(ws_alice, "Alice")  # type: ignore
    await manager.connect(ws_bob, "Bob")  # type: ignore
    await manager.connect(ws_charlie, "Charlie")  # type: ignore

    print(f"[*] Total Active Clients: {manager.connection_count}")
    assert manager.connection_count == 3

    # 2. Topic / Channel Subscriptions
    print("\n[*] Setting up Channel Subscriptions:")
    manager.subscribe("Alice", "alerts")
    manager.subscribe("Bob", "alerts")
    # Charlie is NOT in "alerts", Charlie joins "chat"
    manager.subscribe("Charlie", "chat")

    print(f"    - 'alerts' channel subscribers: {manager.channels['alerts']}")
    print(f"    - 'chat' channel subscribers:   {manager.channels['chat']}")

    # 3. Targeted Direct Messaging
    print("\n[*] Sending direct message from Alice to Bob...")
    direct_msg = WebSocketMessage(
        event=WebSocketEventType.CHAT_MESSAGE,
        sender_id="Alice",
        channel="direct",
        data={"message": "Hey Bob, check the new file upload!"},
    )
    await manager.send_personal_message(direct_msg, "Bob")

    # Bob's inbox should have received the message
    last_bob_msg = json.loads(ws_bob.inbox[-1])
    print(f"    -> Bob received direct message: {last_bob_msg['data']['message']}")
    assert last_bob_msg["data"]["message"] == "Hey Bob, check the new file upload!"

    # 4. Channel Broadcast
    print("\n[*] Broadcasting high-priority message to channel 'alerts'...")
    alert_msg = WebSocketMessage(
        event=WebSocketEventType.NOTIFICATION,
        sender_id="system_monitor",
        channel="alerts",
        data={"level": "CRITICAL", "alert": "CPU spike detected"},
    )
    sent_count = await manager.broadcast_to_channel("alerts", alert_msg)
    print(
        f"    -> Reached {sent_count} subscribers (Alice & Bob). Charlie did not receive this."
    )
    assert sent_count == 2

    # 5. Global Broadcast
    print("\n[*] Broadcasting system-wide notification to all connected clients...")
    global_msg = WebSocketMessage(
        event=WebSocketEventType.NOTIFICATION,
        sender_id="server",
        channel="broadcast",
        data={"announcement": "Scheduled maintenance in 10 minutes"},
    )
    all_count = await manager.broadcast(global_msg)
    print(f"    -> Broadcast reached {all_count} clients successfully.")
    assert all_count == 3

    # 6. Disconnect Handling
    print("\n[*] Disconnecting Charlie...")
    await manager.disconnect("Charlie")
    print(f"[*] Remaining active connections: {manager.connection_count}")
    assert manager.connection_count == 2
    assert "Charlie" not in manager.active_connections

    print("\n" + "=" * 70)
    print(
        "[OK] Tutorial 2 Complete: WebSocket ConnectionManager Architecture Mastered!"
    )
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_websocket_simulation())
