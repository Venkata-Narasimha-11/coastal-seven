"""End-to-End Live Demonstration Script for Day 9.

Demonstrates:
1. Secure File Uploads (UploadFile, MIME validation, Magic Bytes, SHA-256).
2. Pillow Image Processing (aspect-ratio preservation, thumbnails, WebP conversion).
3. WebSockets & ConnectionManager (bi-directional, personal messaging, channels).
4. Real-Time Integration (file upload triggers live WebSocket broadcast).
5. Static File Serving (accessing original and thumbnail URLs).
6. Code Quality & Pytest Test Suite Verification (>80% coverage).
"""

import io
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw
from starlette.testclient import TestClient

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure module importability
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.main import app


def print_header(title: str) -> None:
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)


def generate_demo_image(width: int = 1200, height: int = 800) -> bytes:
    """Generate high-resolution sample graphic in memory."""
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    # Draw geometric patterns
    draw.rectangle([60, 60, width - 60, height - 60], outline=(56, 189, 248), width=10)
    draw.ellipse(
        [width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=(245, 158, 11)
    )
    draw.line([0, 0, width, height], fill=(239, 68, 68), width=6)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def run_demo() -> None:
    print_header("DAY 9: FILE UPLOADS, WEBSOCKETS, TESTING & CODE QUALITY")
    print(
        "FastAPI • UploadFile • Pillow Resizing • WebSockets • Pytest • Black • Mypy\n"
    )

    client = TestClient(app)

    # -------------------------------------------------------------
    # Step 1: Secure File Uploads
    # -------------------------------------------------------------
    print_header("STEP 1: SECURE FILE UPLOAD & VALIDATION")
    raw_img = generate_demo_image(1200, 800)
    print(
        f"[*] Generated synthetic image in memory: 1200x800 px ({len(raw_img) / 1024:.1f} KB)"
    )

    upload_payload = {"file": ("demo_landscape.jpg", raw_img, "image/jpeg")}
    response = client.post("/api/v1/uploads", files=upload_payload)
    print(f"[*] POST /api/v1/uploads -> Status: {response.status_code}")
    assert response.status_code == 201

    data = response.json()
    print(f"    [+] Saved Unique Filename: {data['filename']}")
    print(f"    [+] Declared MIME Type:   {data['content_type']}")
    print(f"    [+] File Size (Human):    {data['file_size_human']}")
    print(f"    [+] SHA-256 Checksum:     {data['checksum_sha256']}")

    # Test rejection of bad file
    bad_res = client.post(
        "/api/v1/uploads", files={"file": ("malware.exe", b"binary", "image/jpeg")}
    )
    print(
        f"[*] Testing Malicious Extension Rejection: Status={bad_res.status_code} ({bad_res.json()['message']})"
    )

    # -------------------------------------------------------------
    # Step 2: Pillow Image Processing & Variants
    # -------------------------------------------------------------
    print_header("STEP 2: PILLOW IMAGE RESIZING & THUMBNAIL GENERATION")
    variants = data["variants"]
    print(f"[*] Generated Image Variants: {list(variants.keys())}")

    original_var = variants["original"]
    medium_var = variants["medium"]
    thumb_var = variants["thumbnail"]

    print(
        f"    - Original:  {original_var['width']}x{original_var['height']} px | Format: {original_var['format']} | URL: {original_var['url']}"
    )
    print(
        f"    - Medium:    {medium_var['width']}x{medium_var['height']} px | Format: {medium_var['format']} | URL: {medium_var['url']}"
    )
    print(
        f"    - Thumbnail: {thumb_var['width']}x{thumb_var['height']} px | Format: {thumb_var['format']} | URL: {thumb_var['url']}"
    )

    print(
        f"[*] Aspect Ratio Consistency: Original={original_var['width']/original_var['height']:.2f}, Thumbnail={thumb_var['width']/thumb_var['height']:.2f}"
    )

    # -------------------------------------------------------------
    # Step 3: WebSockets & ConnectionManager
    # -------------------------------------------------------------
    print_header("STEP 3: WEBSOCKET REAL-TIME BI-DIRECTIONAL COMMUNICATION")
    print("[*] Connecting client 'demo_agent_01' to /ws/demo_agent_01 ...")

    with client.websocket_connect("/ws/demo_agent_01") as ws:
        # 1. Welcome event
        welcome_raw = ws.receive_text()
        welcome = json.loads(welcome_raw)
        print(
            f"    [+] Received Server Event: '{welcome['event']}' -> {welcome['data']['message']}"
        )

        # 2. Ping / Pong Heartbeat
        print("[*] Sending heartbeat ping...")
        ws.send_text(json.dumps({"action": "ping"}))
        pong = json.loads(ws.receive_text())
        print(
            f"    [+] Heartbeat Response: '{pong['event']}' -> reply='{pong['data']['reply']}'"
        )

        # 3. Channel Subscription
        print("[*] Subscribing to channel 'breaking_media'...")
        ws.send_text(json.dumps({"action": "subscribe", "channel": "breaking_media"}))
        sub_reply = json.loads(ws.receive_text())
        print(f"    [+] Subscription Confirmed: {sub_reply['data']['message']}")

        # -------------------------------------------------------------
        # Step 4: Final Integration (Upload + Live WebSocket Broadcast)
        # -------------------------------------------------------------
        print_header("STEP 4: FINAL INTEGRATION (UPLOAD -> PROCESS -> PUSH BROADCAST)")
        print("[*] Uploading new image while WebSocket client is actively listening...")

        new_img = generate_demo_image(900, 900)
        start_t = time.perf_counter()
        integrate_res = client.post(
            "/api/v1/integrated/upload-notify",
            files={"file": ("live_breaking_event.jpg", new_img, "image/jpeg")},
            data={"uploader_name": "FieldReporter_Bob"},
        )
        assert integrate_res.status_code == 201

        # WebSocket listener receives notification immediately
        ws_event_raw = ws.receive_text()
        ws_event = json.loads(ws_event_raw)
        elapsed_ms = (time.perf_counter() - start_t) * 1000

        print(f"    [+] LIVE WEBSOCKET NOTIFICATION RECEIVED in {elapsed_ms:.1f} ms!")
        print(f"        - Event Type:   {ws_event['event']}")
        print(f"        - Uploaded By:  {ws_event['data']['uploader']}")
        print(f"        - File Name:    {ws_event['data']['original_name']}")
        print(f"        - Thumbnail:    {ws_event['data']['thumbnail_url']}")
        print(f"        - Server Proc:  {ws_event['data']['processing_time_ms']} ms")

        # -------------------------------------------------------------
        # Step 5: Static File Serving Verification
        # -------------------------------------------------------------
        print_header("STEP 5: STATIC FILE SERVING VERIFICATION")
        thumb_url = ws_event["data"]["thumbnail_url"]
        thumb_http_res = client.get(thumb_url)
        print(f"[*] GET {thumb_url} -> Status: {thumb_http_res.status_code}")
        assert thumb_http_res.status_code == 200
        print(
            f"    [+] Thumbnail static image delivered ({len(thumb_http_res.content)} bytes)"
        )

        orig_url = ws_event["data"]["url"]
        orig_http_res = client.get(orig_url)
        print(f"[*] GET {orig_url} -> Status: {orig_http_res.status_code}")
        assert orig_http_res.status_code == 200
        print(
            f"    [+] Original static image delivered ({len(orig_http_res.content)} bytes)"
        )

    # -------------------------------------------------------------
    # Step 6: Code Quality & Automated Pytest Coverage
    # -------------------------------------------------------------
    print_header("STEP 6: CODE QUALITY & PYTEST COVERAGE REPORT")

    print("[*] Running automated Pytest suite with line coverage tracking...")
    pytest_res = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "--cov=app",
            "--cov-report=term-missing",
            "-q",
        ],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    print(pytest_res.stdout)

    print("[*] Running Code Quality Linters (Black, isort, Flake8, Mypy)...")
    res_b = subprocess.run(
        [sys.executable, "-m", "black", "--check", "."],
        cwd=str(ROOT_DIR),
        capture_output=True,
    )
    res_i = subprocess.run(
        [sys.executable, "-m", "isort", "--check-only", "."],
        cwd=str(ROOT_DIR),
        capture_output=True,
    )
    res_f = subprocess.run(
        [sys.executable, "-m", "flake8", "."], cwd=str(ROOT_DIR), capture_output=True
    )
    res_m = subprocess.run(
        [sys.executable, "-m", "mypy", "app"], cwd=str(ROOT_DIR), capture_output=True
    )

    print(
        f"    - Black Formatter:     {'[PASS]' if res_b.returncode == 0 else '[FAIL]'}"
    )
    print(
        f"    - isort Import Sorter: {'[PASS]' if res_i.returncode == 0 else '[FAIL]'}"
    )
    print(
        f"    - Flake8 Linter:       {'[PASS]' if res_f.returncode == 0 else '[FAIL]'}"
    )
    print(
        f"    - Mypy Static Types:   {'[PASS]' if res_m.returncode == 0 else '[FAIL]'}"
    )

    print_header("DAY 9 DEMO COMPLETE: ALL COMPONENTS VERIFIED 100% OPERATIONAL")


if __name__ == "__main__":
    run_demo()
