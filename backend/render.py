"""
Render service: one cached entry point for every wallpaper image.

Wallpapers are deterministic, so encoded results are cached in memory (bounded
by bytes) and served with immutable HTTP caching. Thumbnails render on a
proportionally scaled canvas, which is ~10x faster than rendering at full size
and downscaling; full-quality renders always use the fixed base resolution so
previews, wallpapers and downloads match exactly.
"""

import os
import threading
from collections import OrderedDict
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps

from pattern_engine import PRESET_PALETTES, PatternType, blend_patterns, generate_pattern, invert_color
from scene_engine import SCENE_DEFINITIONS, SceneType, generate_scene, get_scene_default_palette

MOBILE_BASE = (1290, 2796)
DESKTOP_BASE = (3840, 2160)
MAX_SIDE = 4096
MIN_SIDE = 16
THUMB_MIN_SCALE = 0.2

PATTERN_KEYS = {p.value for p in PatternType}
SCENE_KEYS = {s.value for s in SceneType}

FORMATS = {
    "webp": ("WEBP", "image/webp"),
    "jpeg": ("JPEG", "image/jpeg"),
    "jpg": ("JPEG", "image/jpeg"),
    "png": ("PNG", "image/png"),
}

# Max simultaneous CPU-bound renders. Thumb requests beyond this cap get an
# immediate 503 so the client retries quickly instead of waiting in a long queue.
_MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_RENDERS", "4"))
_render_sem = threading.Semaphore(_MAX_CONCURRENT)


class RenderError(ValueError):
    """Invalid render parameters (maps to HTTP 400/404)."""


class RenderBusy(Exception):
    """Server is at render capacity — maps to HTTP 503."""


@dataclass(frozen=True)
class RenderSpec:
    kind: str  # "pattern" | "scene"
    key: str
    palette: int = -1  # -1 = scene default palette (scenes) / 0 (patterns)
    seed: int = 12345
    inverted: bool = False
    key2: Optional[str] = None  # second pattern for blending
    blend: float = 0.5
    width: int = MOBILE_BASE[0]
    height: int = MOBILE_BASE[1]
    quality: str = "full"  # "thumb" | "full"
    fmt: str = "webp"

    def validated(self) -> "RenderSpec":
        if self.kind not in ("pattern", "scene"):
            raise RenderError("kind must be 'pattern' or 'scene'")
        if self.kind == "pattern" and self.key not in PATTERN_KEYS:
            raise RenderError(f"Unknown pattern '{self.key}'")
        if self.kind == "scene" and self.key not in SCENE_KEYS:
            raise RenderError(f"Unknown scene '{self.key}'")
        if self.key2 is not None and (self.kind != "pattern" or self.key2 not in PATTERN_KEYS):
            raise RenderError(f"Unknown blend pattern '{self.key2}'")
        if not (-1 <= self.palette < len(PRESET_PALETTES)):
            raise RenderError(f"palette must be between -1 and {len(PRESET_PALETTES) - 1}")
        if not (MIN_SIDE <= self.width <= MAX_SIDE and MIN_SIDE <= self.height <= MAX_SIDE):
            raise RenderError(f"width and height must be between {MIN_SIDE} and {MAX_SIDE}")
        if self.quality not in ("thumb", "full"):
            raise RenderError("quality must be 'thumb' or 'full'")
        if self.fmt not in FORMATS:
            raise RenderError("format must be webp, jpeg or png")
        return RenderSpec(
            kind=self.kind, key=self.key, palette=self.palette, seed=self.seed % 2_147_483_647,
            inverted=self.inverted, key2=self.key2, blend=min(1.0, max(0.0, round(self.blend, 2))),
            width=self.width, height=self.height, quality=self.quality, fmt=self.fmt,
        )

    @property
    def base_size(self):
        return DESKTOP_BASE if self.width > self.height else MOBILE_BASE

    @property
    def canvas_size(self):
        bw, bh = self.base_size
        if self.quality == "full":
            return bw, bh
        scale = max(self.width / bw, self.height / bh)
        scale = min(1.0, max(THUMB_MIN_SCALE, scale))
        # Hard cap: thumbnails never render above 270×585 regardless of requested
        # size. The result is upscaled by ImageOps.fit, which is imperceptible
        # at grid card size and cuts render time for heavy generators by ~4×.
        cw = max(MIN_SIDE, round(bw * scale))
        ch = max(MIN_SIDE, round(bh * scale))
        if self.quality == "thumb":
            cw = min(cw, 270)
            ch = min(ch, 585)
        return cw, ch


def scene_colors(key: str, palette: int, inverted: bool):
    if palette >= 0:
        colors = PRESET_PALETTES[palette]["colors"]
    else:
        colors = get_scene_default_palette(key)
    return [invert_color(c) for c in colors] if inverted else list(colors)


def pattern_colors(palette: int, inverted: bool):
    colors = PRESET_PALETTES[max(0, palette)]["colors"]
    return [invert_color(c) for c in colors] if inverted else list(colors)


@lru_cache(maxsize=64)
def _canvas(kind, key, palette, seed, inverted, key2, blend, cw, ch) -> Image.Image:
    """Raw render on the base (or scaled thumbnail) canvas."""
    if kind == "scene":
        return generate_scene(cw, ch, key, scene_colors(key, palette, inverted), seed)
    if key2:
        return blend_patterns(cw, ch, key, key2, max(0, palette), seed, inverted, blend)
    return generate_pattern(cw, ch, key, max(0, palette), seed, inverted)


class _ByteLRU:
    """Thread-safe LRU bounded by total bytes."""

    def __init__(self, budget_bytes: int):
        self.budget = budget_bytes
        self.size = 0
        self.items: "OrderedDict[RenderSpec, bytes]" = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self.lock:
            value = self.items.get(key)
            if value is None:
                self.misses += 1
                return None
            self.items.move_to_end(key)
            self.hits += 1
            return value

    def put(self, key, value: bytes):
        if len(value) > self.budget // 4:
            return
        with self.lock:
            if key in self.items:
                return
            self.items[key] = value
            self.size += len(value)
            while self.size > self.budget and self.items:
                _, old = self.items.popitem(last=False)
                self.size -= len(old)

    def stats(self):
        with self.lock:
            return {"entries": len(self.items), "bytes": self.size, "hits": self.hits, "misses": self.misses}


_cache = _ByteLRU(512 * 1024 * 1024)
# Concurrent requests for the same image wait for one render instead of
# rendering it several times (a grid often asks for the same thumbnail twice).
_inflight_lock = threading.Lock()
_inflight: "dict[RenderSpec, threading.Lock]" = {}

# Disk cache for thumbnails — survives server restarts so warm-up is instant.
_DISK_CACHE_DIR = Path(os.getenv("THUMB_CACHE_DIR", "/tmp/wallbloom_thumbs"))
_DISK_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _disk_key(spec: RenderSpec) -> Path:
    import hashlib
    h = hashlib.sha1(repr(spec).encode()).hexdigest()[:24]
    return _DISK_CACHE_DIR / f"{h}.{spec.fmt}"


def _disk_get(spec: RenderSpec) -> Optional[bytes]:
    p = _disk_key(spec)
    try:
        return p.read_bytes() if p.exists() else None
    except OSError:
        return None


def _disk_put(spec: RenderSpec, data: bytes) -> None:
    try:
        _disk_key(spec).write_bytes(data)
    except OSError:
        pass


def encode(image: Image.Image, fmt: str, quality: str) -> bytes:
    pil_format, _ = FORMATS[fmt]
    buffer = BytesIO()
    if pil_format == "WEBP":
        image.save(buffer, format="WEBP", quality=80 if quality == "thumb" else 92, method=4)
    elif pil_format == "JPEG":
        image.save(buffer, format="JPEG", quality=85 if quality == "thumb" else 94, optimize=True, progressive=True)
    else:
        image.save(buffer, format="PNG", compress_level=6)
    return buffer.getvalue()


def render(spec: RenderSpec) -> bytes:
    spec = spec.validated()

    # 1. Memory cache — fastest, no I/O
    cached = _cache.get(spec)
    if cached is not None:
        return cached

    # 2. Disk cache — survives restarts, serves thumbs in <1 ms after first render
    if spec.quality == "thumb":
        on_disk = _disk_get(spec)
        if on_disk is not None:
            _cache.put(spec, on_disk)  # promote to memory
            return on_disk

    # 3. CPU render — acquire semaphore or return 503 immediately
    if not _render_sem.acquire(blocking=False):
        raise RenderBusy("Server is busy rendering; please retry in a moment")

    with _inflight_lock:
        lock = _inflight.setdefault(spec, threading.Lock())
    try:
        with lock:
            # Another thread may have finished while we waited for the per-spec lock
            cached = _cache.get(spec)
            if cached is not None:
                return cached
            cw, ch = spec.canvas_size
            image = _canvas(spec.kind, spec.key, spec.palette, spec.seed, spec.inverted, spec.key2, spec.blend, cw, ch)
            if image.size != (spec.width, spec.height):
                image = ImageOps.fit(image, (spec.width, spec.height), Image.LANCZOS, centering=(0.5, 0.5))
            data = encode(image.convert("RGB"), spec.fmt, spec.quality)
            _cache.put(spec, data)
            if spec.quality == "thumb":
                _disk_put(spec, data)
            return data
    finally:
        _render_sem.release()
        with _inflight_lock:
            _inflight.pop(spec, None)


def media_type(fmt: str) -> str:
    return FORMATS[fmt][1]


def etag(spec: RenderSpec) -> str:
    import hashlib

    return '"' + hashlib.sha1(repr(spec.validated()).encode()).hexdigest()[:20] + '"'


def cache_stats():
    return _cache.stats()


def scene_default_colors(key: str):
    return list(SCENE_DEFINITIONS[SceneType(key)]["default_palette"])
