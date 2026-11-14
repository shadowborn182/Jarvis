"""
JARVIS — Pillow Welcome & Goodbye Banner Generator with Safe Image URL Validation
Developer: Shadow
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from io import BytesIO
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from core.branding import parse_hex_color

logger = logging.getLogger("JARVIS.Banners")

BANNER_WIDTH: Final[int] = 1000
BANNER_HEIGHT: Final[int] = 360
MAX_IMAGE_BYTES: Final[int] = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_CONTENT_TYPES: Final[frozenset[str]] = frozenset(
    {"image/png", "image/jpeg", "image/jpg", "image/webp"}
)
ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({".png", ".jpg", ".jpeg", ".webp"})
VALID_TEXT_POSITIONS: Final[tuple[str, ...]] = ("top", "center", "bottom")


def validate_image_url(url: str) -> tuple[bool, str | None]:
    """
    Validate user-supplied image URLs:
    - Require HTTPS scheme.
    - Reject local/private/loopback/link-local hostnames & IPs (SSRF protection).
    - Enforce safe image extension when path ends in a file extension.
    """
    cleaned = url.strip()
    if len(cleaned) > 512:
        return False, "Image URL must be 512 characters or fewer."

    parsed = urlparse(cleaned)
    if parsed.scheme.lower() != "https":
        return False, "Only `https://` image URLs are allowed."

    hostname = (parsed.hostname or "").lower()
    if not hostname or hostname in {"localhost", "0.0.0.0"} or hostname.endswith(".local"):
        return False, "Local or internal hostnames are not permitted."

    try:
        ip_obj = ipaddress.ip_address(hostname)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
            or ip_obj.is_multicast
        ):
            return False, "Private or reserved IP addresses are not permitted."
    except ValueError:
        # Domain name: resolve cautiously if possible, fail closed only on explicitly private resolution
        try:
            resolved_ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            if (
                resolved_ip.is_private
                or resolved_ip.is_loopback
                or resolved_ip.is_link_local
                or resolved_ip.is_reserved
            ):
                return False, "Image URL resolves to a restricted internal IP address."
        except OSError:
            pass

    path_lower = parsed.path.lower()
    if "." in Path(path_lower).name:
        ext = Path(path_lower).suffix
        if ext not in ALLOWED_EXTENSIONS:
            return False, "Allowed image formats: PNG, JPG, JPEG, WEBP."

    return True, None


async def fetch_safe_image(url: str, max_bytes: int = MAX_IMAGE_BYTES) -> Image.Image | None:
    """Download an image safely with strict timeout, MIME type, and size caps."""
    ok, _ = validate_image_url(url)
    if not ok:
        return None

    timeout = aiohttp.ClientTimeout(total=8)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=False) as resp:
                if resp.status != 200:
                    return None
                ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                if ctype and ctype not in ALLOWED_CONTENT_TYPES:
                    return None
                content_length = resp.headers.get("Content-Length")
                if content_length and content_length.isdigit() and int(content_length) > max_bytes:
                    return None

                buf = bytearray()
                async for chunk in resp.content.iter_chunked(65536):
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        return None

        img = Image.open(BytesIO(bytes(buf)))
        img.load()
        return img.convert("RGBA")
    except Exception as exc:
        logger.warning("Failed to fetch custom banner image: %s", exc)
        return None


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:\\Windows\\Fonts\\segoeuib.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_str: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    parsed = parse_hex_color(hex_str)
    if parsed is None:
        return fallback
    val = parsed[1]
    return ((val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF)


def _create_default_background(accent_rgb: tuple[int, int, int]) -> Image.Image:
    """Create a sleek dark gradient background template."""
    img = Image.new("RGBA", (BANNER_WIDTH, BANNER_HEIGHT), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Subtle vertical gradient
    for y in range(BANNER_HEIGHT):
        t = y / BANNER_HEIGHT
        r = int(11 + t * 10)
        g = int(17 + t * 14)
        b = int(32 + t * 22)
        draw.line([(0, y), (BANNER_WIDTH, y)], fill=(r, g, b, 255))

    # Subtle accent bar at top & bottom edge
    draw.rectangle([0, 0, BANNER_WIDTH, 6], fill=(*accent_rgb, 255))
    draw.rectangle([32, 32, BANNER_WIDTH - 32, BANNER_HEIGHT - 32], outline=(51, 65, 85, 180), width=2)
    return img


def _circle_crop(image: Image.Image, size: int, border_rgb: tuple[int, int, int]) -> Image.Image:
    resized = image.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, size - 1, size - 1], fill=255)

    out = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(out)
    border_draw.ellipse([0, 0, size + 11, size + 11], fill=(*border_rgb, 255))
    out.paste(resized, (6, 6), mask)
    return out


async def render_welcome_goodbye_banner(
    *,
    kind: str,
    username: str,
    server_name: str,
    member_count: int,
    avatar_bytes: bytes | None = None,
    server_icon_bytes: bytes | None = None,
    bg_url: str | None = None,
    server_logo_url: str | None = None,
    custom_text: str | None = None,
    text_color: str = "#F8FAFC",
    accent_color: str = "#38BDF8",
    text_position: str = "center",
) -> BytesIO:
    """
    Generate a high-resolution 1000x360 PNG welcome or goodbye banner using Pillow.
    Returns a seeked BytesIO PNG buffer ready for discord.File or FastAPI StreamingResponse.
    """
    text_rgb = _hex_to_rgb(text_color, (248, 250, 252))
    accent_rgb = _hex_to_rgb(accent_color, (56, 189, 248) if kind == "welcome" else (245, 158, 11))

    # 1. Background
    bg_img = await fetch_safe_image(bg_url) if bg_url else None
    if bg_img is not None:
        bg_img = bg_img.resize((BANNER_WIDTH, BANNER_HEIGHT), Image.Resampling.LANCZOS)
        # Apply dark readability scrim over custom background
        scrim = Image.new("RGBA", (BANNER_WIDTH, BANNER_HEIGHT), (10, 15, 28, 165))
        canvas = Image.alpha_composite(bg_img, scrim)
    else:
        canvas = _create_default_background(accent_rgb)

    draw = ImageDraw.Draw(canvas)

    # 2. Member Avatar (left side)
    avatar_size = 180
    avatar_x = 76
    avatar_y = (BANNER_HEIGHT - (avatar_size + 12)) // 2
    if avatar_bytes:
        try:
            av_img = Image.open(BytesIO(avatar_bytes))
            av_circle = _circle_crop(av_img, avatar_size, accent_rgb)
            canvas.paste(av_circle, (avatar_x, avatar_y), av_circle)
        except Exception:
            draw.ellipse(
                [avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size],
                fill=(30, 41, 59, 255),
                outline=(*accent_rgb, 255),
                width=5,
            )
    else:
        draw.ellipse(
            [avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size],
            fill=(30, 41, 59, 255),
            outline=(*accent_rgb, 255),
            width=5,
        )

    # 3. Optional Server Logo (top-right corner)
    logo_img: Image.Image | None = None
    if server_logo_url:
        logo_img = await fetch_safe_image(server_logo_url)
    elif server_icon_bytes:
        try:
            logo_img = Image.open(BytesIO(server_icon_bytes))
        except Exception:
            logo_img = None

    if logo_img is not None:
        logo_circle = _circle_crop(logo_img, 64, (51, 65, 85))
        canvas.paste(logo_circle, (BANNER_WIDTH - 122, 48), logo_circle)

    # 4. Typography & Vertical Positioning
    pos = text_position.lower() if text_position.lower() in VALID_TEXT_POSITIONS else "center"
    base_y = {"top": 64, "center": 108, "bottom": 152}[pos]
    text_x = 300

    font_tag = _load_font(20, bold=True)
    font_name = _load_font(42, bold=True)
    font_sub = _load_font(24, bold=False)
    font_meta = _load_font(19, bold=False)

    tag_label = "WELCOME TO THE SERVER" if kind == "welcome" else "MEMBER DEPARTED"
    default_sub = (
        f"Welcome to {server_name}!"
        if kind == "welcome"
        else f"Goodbye from {server_name}."
    )
    rendered_sub = (
        (custom_text or default_sub)
        .replace("{user}", username)
        .replace("{server}", server_name)
        .replace("{member_count}", str(member_count))
    )[:64]

    display_username = username[:24]
    meta_text = f"{server_name[:32]}  •  Member #{member_count:,}"

    draw.text((text_x, base_y), tag_label, font=font_tag, fill=(*accent_rgb, 255))
    draw.text((text_x, base_y + 32), display_username, font=font_name, fill=(*text_rgb, 255))
    draw.text((text_x, base_y + 90), rendered_sub, font=font_sub, fill=(*text_rgb, 235))
    draw.text((text_x, base_y + 132), meta_text, font=font_meta, fill=(148, 163, 184, 255))

    # Subtle bottom-right JARVIS attribution
    font_brand = _load_font(15, bold=False)
    draw.text(
        (BANNER_WIDTH - 245, BANNER_HEIGHT - 56),
        "JARVIS • Developed by Shadow",
        font=font_brand,
        fill=(148, 163, 184, 200),
    )

    output = BytesIO()
    canvas.convert("RGB").save(output, format="PNG", optimize=True)
    output.seek(0)
    return output
