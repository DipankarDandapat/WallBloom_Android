"""
WallBloom - procedural wallpaper generator backend
FastAPI application - NO AUTHENTICATION (open access)

v1 endpoints are kept for older app builds. v2 adds a dynamic catalog, a
curated feed and a single cached render endpoint used by the current app.

Rendering handlers are plain `def` functions on purpose: FastAPI runs them in
its thread pool, so CPU-bound image work never blocks the event loop.
"""

import logging
import os
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

import catalog as catalog_module
import render as render_service
from pattern_engine import PRESET_PALETTES, PatternType
from render import DESKTOP_BASE, MOBILE_BASE, RenderError, RenderSpec
from scene_engine import SCENE_DEFINITIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_VERSION = "2.0.0"
IMMUTABLE = "public, max-age=31536000, immutable"


def _warm_cache():
    """Pre-render today's hero and first feed page thumbnails after start-up."""
    try:
        items = catalog_module.hero() + catalog_module.feed(page=0, page_size=12)
        for item in items:
            render_service.render(RenderSpec(kind=item["kind"], key=item["key"], palette=item["palette"],
                                             seed=item["seed"], width=540, height=1170, quality="thumb"))
        logger.info("✓ Warmed %d thumbnails", len(items))
    except Exception:  # warm-up is best effort
        logger.exception("Cache warm-up failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✓ WallBloom Backend Started")
    if os.getenv("WARM_CACHE", "1") == "1":
        threading.Thread(target=_warm_cache, daemon=True).start()
    yield
    logger.info("✓ WallBloom Backend Shutdown")


app = FastAPI(
    title="WallBloom API",
    description="Procedural wallpaper generator backend",
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RenderError)
async def render_error_handler(_: Request, exc: RenderError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


def _image_response(spec: RenderSpec, request: Request, filename: Optional[str] = None) -> Response:
    tag = render_service.etag(spec)
    headers = {"Cache-Control": IMMUTABLE, "ETag": tag}
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers=headers)
    data = render_service.render(spec)
    disposition = "attachment" if filename else "inline"
    headers["Content-Disposition"] = f"{disposition}; filename={filename or 'wallpaper.' + spec.fmt}"
    return Response(content=data, media_type=render_service.media_type(spec.fmt), headers=headers)


# ============================================================================
# Health
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "WallBloom Backend",
        "version": API_VERSION,
    }


@app.get("/")
async def root():
    return {
        "name": "WallBloom API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "catalog": "/api/v2/catalog",
        "feed": "/api/v2/feed",
        "render": "/api/v2/render",
    }


# ============================================================================
# v2 API
# ============================================================================

@app.get("/api/v2/catalog")
def get_catalog():
    """Everything the app renders as navigation/content: categories, icons, themes, palettes, collections."""
    return JSONResponse(catalog_module.catalog(), headers={"Cache-Control": "public, max-age=1800"})


@app.get("/api/v2/feed")
def get_feed(
    collection: Optional[str] = Query(None, description="Collection id; omit for the mixed Discover feed"),
    page: int = Query(0, ge=0, le=10_000),
    page_size: int = Query(24, ge=1, le=60),
    salt: Optional[int] = Query(None, description="Override the daily seed (e.g. pull-to-refresh)"),
):
    if collection and collection not in catalog_module.COLLECTIONS_BY_ID:
        raise HTTPException(status_code=404, detail=f"Unknown collection '{collection}'")
    items = catalog_module.feed(collection, page, page_size, salt)
    return JSONResponse(
        {"collection": collection, "page": page, "page_size": page_size, "next_page": page + 1, "items": items},
        headers={"Cache-Control": "public, max-age=600"},
    )


@app.get("/api/v2/render")
def render_v2(
    request: Request,
    kind: str = Query(..., pattern="^(pattern|scene)$"),
    key: str = Query(...),
    palette: int = Query(-1),
    seed: int = Query(12345),
    inverted: bool = Query(False),
    key2: Optional[str] = Query(None),
    blend: float = Query(0.5),
    w: int = Query(MOBILE_BASE[0]),
    h: int = Query(MOBILE_BASE[1]),
    quality: str = Query("full"),
    fmt: str = Query("webp"),
    download: bool = Query(False),
):
    """Render any wallpaper at any size. `quality=thumb` is fast for grids; `full` matches downloads exactly."""
    spec = RenderSpec(kind=kind, key=key, palette=palette, seed=seed, inverted=inverted, key2=key2 or None,
                      blend=blend, width=w, height=h, quality=quality, fmt=fmt)
    filename = f"wallbloom_{key}_{w}x{h}_{seed}.{fmt}" if download else None
    return _image_response(spec, request, filename)


@app.get("/api/v2/stats")
def stats():
    return {"cache": render_service.cache_stats()}


# ============================================================================
# v1 API (compatibility)
# ============================================================================

class GenerateWallpaperRequest(BaseModel):
    pattern_type: str
    palette_index: int
    seed: int
    inverted: bool = False


@app.get("/api/patterns")
async def list_patterns():
    return {
        "patterns": [
            {"type": p.value, "name": catalog_module.pattern_name(p.value),
             "description": f"A {p.value.replace('_', ' ')} pattern"}
            for p in PatternType
        ]
    }


@app.get("/api/palettes")
async def list_palettes():
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"id": i, "name": p.get("name", f"Palette {i + 1}"), "colors": p["colors"],
         "description": f"Palette: {p.get('name', i)}", "is_preset": True, "created_at": now, "updated_at": now}
        for i, p in enumerate(PRESET_PALETTES)
    ]


@app.post("/api/wallpapers/generate")
async def generate_wallpaper(request: GenerateWallpaperRequest):
    if request.pattern_type not in render_service.PATTERN_KEYS:
        raise HTTPException(status_code=404, detail=f"Unknown pattern '{request.pattern_type}'")
    now = datetime.now(timezone.utc).isoformat()
    return {"id": request.seed % 10000, "pattern_type": request.pattern_type, "palette_index": request.palette_index,
            "seed": request.seed, "inverted": request.inverted, "created_at": now, "updated_at": now}


@app.get("/api/scenes")
async def list_scenes():
    themes = {}
    for scene_type, scene_def in SCENE_DEFINITIONS.items():
        theme_id = scene_def["theme"].value
        meta = catalog_module.SCENE_THEMES.get(theme_id, {})
        group = themes.setdefault(theme_id, {"id": theme_id, "name": meta.get("name", theme_id.title()),
                                              "emoji": meta.get("emoji", "🎨"), "scenes": []})
        group["scenes"].append({"id": scene_type.value, "name": scene_def["name"], "theme": theme_id,
                                "emoji": scene_def["emoji"]})
    return {"themes": list(themes.values())}


@app.get("/api/wallpapers/scene")
def get_scene_wallpaper(
    request: Request,
    scene_type: str = Query("eiffel_tower"),
    seed: int = Query(12345),
    inverted: bool = Query(False),
    width: int = Query(800),
    height: int = Query(600),
    palette_override: int = Query(-1),
):
    spec = RenderSpec(kind="scene", key=scene_type, palette=palette_override, seed=seed, inverted=inverted,
                      width=width, height=height, quality="full", fmt="png")
    return _image_response(spec, request)


@app.get("/api/wallpapers/preview")
def get_wallpaper_preview(
    request: Request,
    pattern_type: str = Query("hills"),
    palette_index: int = Query(0),
    seed: int = Query(12345),
    inverted: bool = Query(False),
    width: int = Query(800),
    height: int = Query(600),
    pattern_type_2: Optional[str] = Query(None),
    blend_ratio: float = Query(0.5),
):
    spec = RenderSpec(kind="pattern", key=pattern_type, palette=max(0, palette_index), seed=seed, inverted=inverted,
                      key2=pattern_type_2, blend=blend_ratio, width=width, height=height, quality="full", fmt="png")
    return _image_response(spec, request)


def _v1_download(request, device, pattern_type, palette_index, seed, inverted, pattern_type_2, blend_ratio,
                 scene_type, palette_override):
    width, height = DESKTOP_BASE if device == "desktop" else MOBILE_BASE
    if scene_type:
        spec = RenderSpec(kind="scene", key=scene_type, palette=palette_override, seed=seed, inverted=inverted,
                          width=width, height=height, fmt="png")
    else:
        spec = RenderSpec(kind="pattern", key=pattern_type, palette=max(0, palette_index), seed=seed,
                          inverted=inverted, key2=pattern_type_2, blend=blend_ratio, width=width, height=height,
                          fmt="png")
    return _image_response(spec, request, f"wallbloom_{device}_{seed}.png")


@app.get("/api/wallpapers/download/desktop")
def download_desktop_wallpaper(
    request: Request,
    pattern_type: str = Query("hills"),
    palette_index: int = Query(0),
    seed: int = Query(12345),
    inverted: bool = Query(False),
    pattern_type_2: Optional[str] = Query(None),
    blend_ratio: float = Query(0.5),
    scene_type: Optional[str] = Query(None),
    palette_override: int = Query(-1),
):
    return _v1_download(request, "desktop", pattern_type, palette_index, seed, inverted, pattern_type_2,
                        blend_ratio, scene_type, palette_override)


@app.get("/api/wallpapers/download/mobile")
def download_mobile_wallpaper(
    request: Request,
    pattern_type: str = Query("hills"),
    palette_index: int = Query(0),
    seed: int = Query(12345),
    inverted: bool = Query(False),
    pattern_type_2: Optional[str] = Query(None),
    blend_ratio: float = Query(0.5),
    scene_type: Optional[str] = Query(None),
    palette_override: int = Query(-1),
):
    return _v1_download(request, "mobile", pattern_type, palette_index, seed, inverted, pattern_type_2,
                        blend_ratio, scene_type, palette_override)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info",
    )
