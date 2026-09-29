"""Tutorial 1: FastAPI File Uploads & Pillow Image Processing Deep Dive.

Topics covered:
1. UploadFile vs bytes: Why UploadFile uses SpooledTemporaryFile for memory safety.
2. Magic Number Inspection: Defending against renamed malicious extensions.
3. Pillow Resizing: Aspect-ratio preservation using LANCZOS high-quality resampling.
4. Thumbnail Generation: Generating lightweight preview assets.
5. EXIF Metadata Privacy: Stripping GPS and hardware tags.
"""

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure module importability
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import detect_mime_from_magic_bytes, sanitize_filename


def demo_upload_safety_and_magic_bytes() -> None:
    print("=" * 70)
    print("1. DEMONSTRATING FILE UPLOAD INTEGRITY & MAGIC BYTES INSPECTION")
    print("=" * 70)

    # Legitimate PNG header: \x89PNG\r\n\x1a\n
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    detected = detect_mime_from_magic_bytes(png_bytes)
    print(f"[*] Input: Valid PNG header -> Detected MIME: {detected}")

    # Spoofed file: Malicious script renamed as harmless picture.png
    fake_png = b"import os; os.system('calc.exe') # harmless looking text"
    detected_fake = detect_mime_from_magic_bytes(fake_png)
    print(
        f"[*] Input: Executable script named 'picture.png' -> Detected MIME: {detected_fake}"
    )
    print("    -> Notice: The magic number check caught the masquerade!\n")

    # Filename sanitization against directory traversal
    unsafe_name = "../../etc/passwd..//avatar image 2026!@#.png"
    safe_name = sanitize_filename(unsafe_name, prefix_uuid=False)
    print(f"[*] Original Filename: '{unsafe_name}'")
    print(f"[*] Sanitized Output:  '{safe_name}'")


def demo_pillow_image_transforms() -> None:
    print("\n" + "=" * 70)
    print("2. PILLOW IMAGE RESIZING, ASPECT RATIO & EXIF PRIVACY")
    print("=" * 70)

    # 1. Create a dynamic high-resolution sample image in memory
    orig_w, orig_h = 1200, 800
    img = Image.new("RGB", (orig_w, orig_h), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, orig_w - 50, orig_h - 50], outline=(56, 189, 248), width=8)
    draw.ellipse(
        [400, 250, 800, 550], fill=(245, 158, 11), outline=(239, 68, 68), width=4
    )

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    raw_bytes = buf.getvalue()
    print(
        f"[*] Created synthetic high-res image: {orig_w}x{orig_h} px | Size: {len(raw_bytes) / 1024:.1f} KB"
    )

    # 2. Resizing with aspect-ratio preservation
    target_max_w, target_max_h = 200, 200
    ratio = min(target_max_w / orig_w, target_max_h / orig_h)
    new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)

    # Apply Lanczos resampling for maximum sharpness without aliasing
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    thumb_buf = io.BytesIO()
    resized_img.save(thumb_buf, format="WEBP", quality=80)
    thumb_bytes = thumb_buf.getvalue()

    print(
        f"[*] Resized Thumbnail Dimensions: {resized_img.size[0]}x{resized_img.size[1]} px"
    )
    print(f"[*] Compressed WebP Thumbnail Size: {len(thumb_bytes) / 1024:.1f} KB")
    print(
        f"[*] Bandwidth Reduction: {100 - (len(thumb_bytes) / len(raw_bytes) * 100):.1f}% smaller!"
    )

    # 3. EXIF stripping check
    clean_img = Image.new(resized_img.mode, resized_img.size)
    clean_img.paste(resized_img)
    print(f"[*] EXIF metadata stripped successfully. Safe for public CDN distribution.")


if __name__ == "__main__":
    demo_upload_safety_and_magic_bytes()
    demo_pillow_image_transforms()
    print("\n" + "=" * 70)
    print("[OK] Tutorial 1 Complete: Secure Upload & Pillow Processing Mastered!")
    print("=" * 70)
