import json

from starlette.testclient import TestClient


def test_websocket_connect_and_welcome(client: TestClient) -> None:
    """Test connecting to /ws/{client_id} receives initial welcome notification."""
    with client.websocket_connect("/ws/client_alpha") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["event"] == "notification"
        assert msg["sender_id"] == "server"
        assert "Welcome, client 'client_alpha'" in msg["data"]["message"]


def test_websocket_ping_pong_heartbeat(client: TestClient) -> None:
    """Test ping message triggers heartbeat pong reply."""
    with client.websocket_connect("/ws/client_pinger") as ws:
        _ = ws.receive_text()  # Drain welcome

        ws.send_text(json.dumps({"action": "ping"}))
        reply = json.loads(ws.receive_text())

        assert reply["event"] == "heartbeat"
        assert reply["data"]["reply"] == "pong"


def test_websocket_channel_subscribe_unsubscribe(client: TestClient) -> None:
    """Test subscribing and unsubscribing from topics."""
    with client.websocket_connect("/ws/subscriber_user") as ws:
        _ = ws.receive_text()  # Drain welcome

        # Subscribe
        ws.send_text(json.dumps({"action": "subscribe", "channel": "news"}))
        sub_reply = json.loads(ws.receive_text())
        assert sub_reply["event"] == "notification"
        assert "Subscribed to channel: news" in sub_reply["data"]["message"]

        # Unsubscribe
        ws.send_text(json.dumps({"action": "unsubscribe", "channel": "news"}))
        unsub_reply = json.loads(ws.receive_text())
        assert unsub_reply["event"] == "notification"
        assert "Unsubscribed from channel: news" in unsub_reply["data"]["message"]


def test_websocket_direct_message(client: TestClient) -> None:
    """Test direct message between two active WebSocket clients."""
    with client.websocket_connect("/ws/sender_client") as ws_sender:
        _ = ws_sender.receive_text()

        with client.websocket_connect("/ws/receiver_client") as ws_receiver:
            _ = ws_receiver.receive_text()

            # Drain any client_connected notifications
            # Sender transmits direct message to receiver
            ws_sender.send_text(
                json.dumps(
                    {
                        "action": "direct_message",
                        "target_id": "receiver_client",
                        "message": "Private hello from sender!",
                    }
                )
            )

            received = json.loads(ws_receiver.receive_text())
            # Could be client_connected or chat_message; loop if notification
            if received["event"] != "chat_message":
                received = json.loads(ws_receiver.receive_text())

            assert received["event"] == "chat_message"
            assert received["data"]["message"] == "Private hello from sender!"
            assert received["data"]["from"] == "sender_client"


def test_websocket_direct_message_offline_target(client: TestClient) -> None:
    """Test error message when messaging an offline client."""
    with client.websocket_connect("/ws/sender_alone") as ws:
        _ = ws.receive_text()

        ws.send_text(
            json.dumps(
                {
                    "action": "direct_message",
                    "target_id": "ghost_client_404",
                    "message": "Are you there?",
                }
            )
        )

        error_reply = json.loads(ws.receive_text())
        assert error_reply["event"] == "error"
        assert "is offline" in error_reply["data"]["error"]


def test_websocket_dedicated_channel_endpoint(client: TestClient) -> None:
    """Test connecting directly to /ws/channel/{channel_name}/{client_id}."""
    with client.websocket_connect("/ws/channel/finance/client_trader") as ws:
        welcome = json.loads(ws.receive_text())
        assert welcome["event"] == "notification"
        assert "Connected to dedicated channel 'finance'" in welcome["data"]["message"]


def test_http_broadcast_api(client: TestClient) -> None:
    """Test HTTP API /api/v1/ws/broadcast sends event to connected WebSocket."""
    with client.websocket_connect("/ws/listener_for_http") as ws:
        _ = ws.receive_text()

        http_res = client.post(
            "/api/v1/ws/broadcast",
            json={"message": "System wide alert!", "channel": "broadcast"},
        )
        assert http_res.status_code == 200
        assert http_res.json()["success"] is True

        ws_msg = json.loads(ws.receive_text())
        assert ws_msg["event"] == "notification"
        assert ws_msg["data"]["message"] == "System wide alert!"


def test_get_connected_clients_api(client: TestClient) -> None:
    """Test GET /api/v1/ws/clients lists active connections."""
    with client.websocket_connect("/ws/active_query_client"):
        res = client.get("/api/v1/ws/clients")
        assert res.status_code == 200
        clients = res.json()
        assert any(c["client_id"] == "active_query_client" for c in clients)
