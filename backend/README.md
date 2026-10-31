# WallBloom backend (FastAPI)

Stateless, deterministic wallpaper renderer. No authentication, no database.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt    # runtime deps + pytest/httpx
python main.py                         # PORT (default 8000), DEBUG=true enables reload
python -m pytest -q
```

Environment variables: `PORT`, `DEBUG` (`true` enables auto-reload), `WARM_CACHE` (`1` by default; pre-renders today's hero and first feed page in the background after start-up).

## Modules

| File | Role |
|---|---|
| `pattern_engine.py` | 98 original procedural patterns + 70 palettes. Hot spots (`contour`, `topographic`, `aurora`, `voronoi`, `stained_glass`) are vectorised with numpy and produce pixel-identical output 4–200× faster. |
| `scene_engine.py` | 74 original illustrated scenes in 7 themes + the Minimal theme registered from `premium_engine`. |
| `premium_engine.py` | Gradient/blur/grain based generators: 9 patterns and 9 Minimal scenes. |
| `render.py` | Single render entry point: validation, thumbnail scaling, cover-fit to any size, WebP/JPEG/PNG encoding, byte-bounded LRU cache and request coalescing. |
| `catalog.py` | Pattern categories, scene-theme metadata, palette tags, collections and the deterministic daily feed. |
| `main.py` | HTTP routes (v2 + v1 compatibility). |

## v2 API

### `GET /api/v2/catalog`

Everything the app shows as navigation and content: `pattern_categories` (id, name, Material Symbols `icon`, `emoji` fallback, `accent`), `patterns` (key, name, category, glyph, featured), `scene_themes` with their scenes and default colours, `palettes` with tags, `collections` (with a cover wallpaper) and today's `hero` wallpapers. Cached for 30 minutes.

### `GET /api/v2/feed?collection=&page=&page_size=&salt=`

An infinite, deterministic, curated feed. Without `collection` it mixes featured patterns and scenes; `salt` reshuffles it (pull-to-refresh). The default salt changes daily. Unknown collections return 404.

Each item is a complete wallpaper description:

```json
{"id": "scene:ocean_sunset:-1:438211:0", "kind": "scene", "key": "ocean_sunset", "name": "Ocean Sunset",
 "subtitle": "Minimal", "category": "minimal", "palette": -1, "seed": 438211, "inverted": false,
 "colors": ["#120d26", "..."]}
```

### `GET /api/v2/render`

| Param | Meaning |
|---|---|
| `kind` | `pattern` or `scene` |
| `key` | Pattern or scene key |
| `palette` | Palette id; `-1` = the scene's own palette |
| `seed`, `inverted` | Variation and colour inversion (inversion now also applies to default scene palettes) |
| `key2`, `blend` | Optional second pattern blended in (patterns only) |
| `w`, `h` | Output size, 16–4096. Landscape sizes use the 3840×2160 base, portrait sizes use 1290×2796; other aspect ratios are cover-cropped. |
| `quality` | `thumb` renders on a proportionally smaller canvas (fast, for grids); `full` renders at base resolution, so it matches downloads exactly |
| `fmt` | `webp` (default), `jpeg` or `png` |
| `download` | `true` adds `Content-Disposition: attachment` |

Responses are immutable (`Cache-Control: public, max-age=31536000, immutable`) with an `ETag`; invalid parameters return 400.

### `GET /api/v2/stats`

Render cache entries, bytes, hits and misses.

## v1 API (kept for older app builds)

`/health`, `/api/patterns`, `/api/palettes`, `/api/scenes`, `POST /api/wallpapers/generate`, `/api/wallpapers/preview`, `/api/wallpapers/scene`, `/api/wallpapers/download/{desktop|mobile}`. They now go through the same cached renderer, return real HTTP error codes (they previously returned `[{"error": …}, 500]` with status 200), and run in the thread pool instead of blocking the event loop.

## Performance notes

- Render handlers are sync `def`, so FastAPI runs CPU-bound work in its thread pool and health/catalog calls stay responsive during renders.
- Thumbnails (`quality=thumb`) render ~10× faster than downscaling a full render.
- Encoded images are cached in memory (160 MB budget); concurrent requests for the same image wait for a single render.
- Clients and CDNs can cache every image forever because output is deterministic.
