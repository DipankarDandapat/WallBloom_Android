"""
Catalog + curated feed for the v2 API.

Everything the app displays as content - categories, their icons and accent
colours, scene themes, collections and the daily feed - is described here so
the client can change without an app release. Icons are Material Symbols
names; clients map known names and fall back to the emoji.
"""

import colorsys
import random
from datetime import datetime, timezone

from pattern_engine import PRESET_PALETTES, PatternType
from scene_engine import SCENE_DEFINITIONS, SceneTheme, SceneType

# ----------------------------------------------------------------------------
# Patterns
# ----------------------------------------------------------------------------

PATTERN_CATEGORIES = [
    {
        "id": "gradients", "name": "Gradients", "icon": "gradient", "emoji": "🌈", "accent": "#FF7AB6",
        "description": "Soft colour fields, glow and grain",
        "patterns": ["mesh_gradient", "grain_gradient", "liquid", "bokeh", "glass_orbs", "gradient", "plasma",
                     "aurora", "smoke", "watercolor", "lava"],
    },
    {
        "id": "landscapes", "name": "Landscapes", "icon": "landscape", "emoji": "⛰️", "accent": "#5FD3A8",
        "description": "Ridges, dunes and rolling layers",
        "patterns": ["layered_peaks", "silk_waves", "waves", "dunes", "hills", "mountains", "terraces", "tides",
                     "peaks", "sand_ripple", "sandstorm", "clouds", "lenticular"],
    },
    {
        "id": "geometric", "name": "Geometric", "icon": "category", "emoji": "🔷", "accent": "#7C8CFF",
        "description": "Tiles, grids and precise forms",
        "patterns": ["halftone", "geometric", "hexagon", "diamond", "mosaic", "chevron", "origami", "triangular_mesh",
                     "prism", "patchwork", "plaid", "weave", "scales", "polka", "wire_frame", "crystals",
                     "honeycomb_flow", "celtic_knot", "kaleidoscope", "mandala", "pinwheel", "sunburst"],
    },
    {
        "id": "cosmic", "name": "Cosmic", "icon": "auto_awesome", "emoji": "✨", "accent": "#B58CFF",
        "description": "Spirals, stars and hypnotic rings",
        "patterns": ["galaxy", "starburst", "constellation", "meteor_shower", "vortex", "spiral", "hypnotic",
                     "rings", "ripple"],
    },
    {
        "id": "tech", "name": "Tech", "icon": "memory", "emoji": "💻", "accent": "#3DDCFF",
        "description": "Circuits, signals and glitches",
        "patterns": ["circuit", "binary_rain", "radar", "satellite", "sonar", "datastream", "fiber_optic", "neural",
                     "glitch", "pixel_sort", "neon_grid", "waveform", "maze", "labyrinth", "interference",
                     "lightning", "lightning_field"],
    },
    {
        "id": "organic", "name": "Organic", "icon": "eco", "emoji": "🌿", "accent": "#9BD45A",
        "description": "Cells, roots, drops and textures",
        "patterns": ["cellular", "voronoi", "stained_glass", "coral", "snowflakes", "raindrops", "vines", "bamboo",
                     "cracks", "roots", "pebbles", "feathers", "bubbles", "soap_bubble", "droplets", "topsoil",
                     "fish_net", "cobweb", "lace", "dna", "tree_rings", "noodles", "fractal", "turbulence",
                     "ink_blot"],
    },
    {
        "id": "artistic", "name": "Artistic", "icon": "brush", "emoji": "🖌️", "accent": "#FFB35C",
        "description": "Strokes, lines and hand-drawn energy",
        "patterns": ["flow_lines", "contour", "topographic", "brushstroke", "brush_grid", "scribble", "arcs",
                     "crosshatch", "pointillism", "noise"],
    },
]

# Patterns whose output looks great at a glance; the feed draws from these.
FEATURED_PATTERNS = [
    "mesh_gradient", "grain_gradient", "layered_peaks", "silk_waves", "bokeh", "liquid", "flow_lines", "glass_orbs",
    "halftone", "waves", "dunes", "hexagon", "vortex", "diamond", "mosaic", "terraces", "tides", "chevron", "origami",
    "crystals", "scales", "dna", "topographic", "voronoi", "kaleidoscope", "triangular_mesh", "plasma",
    "interference", "turbulence", "stained_glass", "honeycomb_flow", "tree_rings", "lenticular", "patchwork",
    "sunburst", "wire_frame", "mandala", "weave", "lava", "smoke", "pointillism", "pixel_sort", "aurora", "cellular",
]
# Premium patterns get extra weight in the feed.
PREMIUM_WEIGHT = {"mesh_gradient": 4, "grain_gradient": 2, "layered_peaks": 4, "silk_waves": 4, "bokeh": 3,
                  "liquid": 3, "flow_lines": 3, "glass_orbs": 3, "halftone": 2}

PATTERN_GLYPHS = {
    "hills": "⛰", "waves": "🌊", "dunes": "🏜", "mountains": "🗻", "arcs": "🌈", "scribble": "✏️", "geometric": "🔷",
    "noise": "🌫", "gradient": "🎨", "cellular": "🔲", "spiral": "🌀", "hexagon": "⬡", "aurora": "🌌", "mandala": "🪷",
    "vortex": "💫", "lightning": "⚡", "bubbles": "🫧", "diamond": "💎", "lava": "🌋", "circuit": "🔌", "galaxy": "🌠",
    "ripple": "💧", "mosaic": "🪟", "terraces": "🏔", "tides": "🌬", "sandstorm": "🌪", "peaks": "⛰", "rings": "🎯",
    "brushstroke": "🖌", "contour": "🗺", "plaid": "🧣", "starburst": "✨", "weave": "🧺", "pebbles": "🪨",
    "chevron": "〽️", "fractal": "🔺", "cobweb": "🕸", "origami": "📐", "noodles": "🍜", "crystals": "💠",
    "smoke": "💨", "labyrinth": "🌀", "polka": "🔵", "feathers": "🪶", "scales": "🐟", "crosshatch": "✖️", "dna": "🧬",
    "binary_rain": "💻", "radar": "📡", "topographic": "🗾", "waveform": "〰️", "satellite": "🛰️", "sonar": "🔊",
    "datastream": "📊", "fiber_optic": "🔆", "neural": "🧠", "coral": "🪸", "snowflakes": "❄️", "raindrops": "🌧",
    "vines": "🌿", "clouds": "☁️", "bamboo": "🎋", "cracks": "🪨", "roots": "🌱", "voronoi": "🔹",
    "kaleidoscope": "🔮", "triangular_mesh": "📐", "pinwheel": "🎡", "prism": "🔻", "hypnotic": "🌐", "plasma": "⚡",
    "interference": "〰️", "turbulence": "🌪", "ink_blot": "🖋", "watercolor": "🎨", "pointillism": "🔴", "maze": "🧩",
    "constellation": "⭐", "lace": "🕸", "glitch": "📺", "stained_glass": "🪟", "topsoil": "🌾", "fish_net": "🎣",
    "honeycomb_flow": "🍯", "pixel_sort": "🖥️", "sand_ripple": "🏖️", "tree_rings": "🌳", "lightning_field": "⚡",
    "soap_bubble": "🫧", "celtic_knot": "☘️", "meteor_shower": "🌠", "lenticular": "🌈", "brush_grid": "🖌️",
    "neon_grid": "🔲", "patchwork": "🧵", "sunburst": "🌞", "droplets": "💧", "wire_frame": "🕸️",
    "mesh_gradient": "🌈", "grain_gradient": "🎞️", "layered_peaks": "🏔️", "silk_waves": "🎐", "bokeh": "🔆",
    "liquid": "🫗", "flow_lines": "〰️", "glass_orbs": "🔮", "halftone": "⚫",
}

PATTERN_NAMES = {"dna": "DNA", "mesh_gradient": "Mesh Gradient", "grain_gradient": "Grain Gradient",
                 "glass_orbs": "Glass Orbs", "flow_lines": "Flow Lines"}


def pattern_name(key: str) -> str:
    return PATTERN_NAMES.get(key, key.replace("_", " ").title())


def _pattern_category_map():
    mapping = {}
    for category in PATTERN_CATEGORIES:
        for key in category["patterns"]:
            mapping.setdefault(key, category["id"])
    # Anything new that was not categorised lands in "artistic" so it is never hidden.
    for p in PatternType:
        mapping.setdefault(p.value, "artistic")
    return mapping


PATTERN_CATEGORY = _pattern_category_map()

# ----------------------------------------------------------------------------
# Scenes
# ----------------------------------------------------------------------------

SCENE_THEMES = {
    SceneTheme.MINIMAL.value: {"name": "Minimal", "icon": "filter_hdr", "emoji": "🏔️", "accent": "#F4A261",
                               "description": "Atmospheric gradients and quiet horizons"},
    SceneTheme.CELESTIAL.value: {"name": "Celestial", "icon": "nights_stay", "emoji": "🌌", "accent": "#9D8CFF",
                                 "description": "Eclipses, comets and starlit skies"},
    SceneTheme.LANDMARKS.value: {"name": "Landmarks", "icon": "account_balance", "emoji": "🗼", "accent": "#FFB86B",
                                 "description": "Iconic places from around the globe"},
    SceneTheme.WORLD_SCENES.value: {"name": "World", "icon": "public", "emoji": "🌍", "accent": "#58C4DD",
                                    "description": "Deserts, fjords, glaciers and plains"},
    SceneTheme.NATURE_ELEMENTS.value: {"name": "Nature", "icon": "forest", "emoji": "🌿", "accent": "#6FCF97",
                                       "description": "Forests, volcanoes, storms and reefs"},
    SceneTheme.URBAN.value: {"name": "Urban", "icon": "apartment", "emoji": "🌆", "accent": "#FF6FAE",
                             "description": "Skylines, neon streets and night markets"},
    SceneTheme.UNDERWATER.value: {"name": "Underwater", "icon": "water", "emoji": "🐠", "accent": "#3DC9F5",
                                  "description": "Kelp forests, wrecks and bioluminescence"},
    SceneTheme.FANTASY.value: {"name": "Fantasy", "icon": "castle", "emoji": "🏰", "accent": "#C38BFF",
                               "description": "Enchanted forests and floating islands"},
}
THEME_ORDER = [t for t in SCENE_THEMES]

# ----------------------------------------------------------------------------
# Palettes
# ----------------------------------------------------------------------------


def _hex_rgb01(value):
    h = value.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _luma(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def palette_tags(colors):
    rgbs = [_hex_rgb01(c) for c in colors]
    lumas = [_luma(c) for c in rgbs]
    sats = [colorsys.rgb_to_hsv(*c)[1] for c in rgbs]
    mean = sum(lumas) / len(lumas)
    tags = []
    if mean < 0.3:
        tags.append("dark")
    if min(lumas) < 0.015 and mean < 0.3:
        tags.append("amoled")
    if mean > 0.6:
        tags.append("light")
    if max(sats) > 0.75 and max(lumas) > 0.3:
        tags.append("vivid")
    if max(sats) < 0.12:
        tags.append("mono")
    return tags


PALETTES = [
    {"id": i, "name": p.get("name", f"Palette {i + 1}"), "colors": p["colors"], "tags": palette_tags(p["colors"])}
    for i, p in enumerate(PRESET_PALETTES)
]


def _palettes_with(*tags, exclude=("mono",)):
    return [p["id"] for p in PALETTES
            if (not tags or any(t in p["tags"] for t in tags)) and not any(t in p["tags"] for t in exclude)]


ALL_COLOURFUL = _palettes_with()
DARK_PALETTES = _palettes_with("dark", "amoled")
LIGHT_PALETTES = _palettes_with("light")
VIVID_PALETTES = _palettes_with("vivid")


def _scene_is_dark(key):
    colors = SCENE_DEFINITIONS[SceneType(key)]["default_palette"]
    lumas = sorted(_luma(_hex_rgb01(c)) for c in colors)
    return lumas[0] < 0.06 and sum(lumas[:3]) / 3 < 0.2


def _scenes_in(*themes):
    return [s.value for s, d in SCENE_DEFINITIONS.items() if d["theme"].value in themes]


# ----------------------------------------------------------------------------
# Collections (feed filters)
# ----------------------------------------------------------------------------
# Each collection is a pool of (kind, key, palettes, weight) templates.

def _pattern_pool(keys, palettes, weight=1):
    return [("pattern", k, palettes, weight * PREMIUM_WEIGHT.get(k, 1)) for k in keys]


def _scene_pool(keys, weight=1, palettes=(-1,)):
    return [("scene", k, list(palettes), weight * (3 if SCENE_DEFINITIONS[SceneType(k)]["theme"] == SceneTheme.MINIMAL else 1))
            for k in keys]


def _featured_in(*categories):
    return [k for k in FEATURED_PATTERNS if PATTERN_CATEGORY[k] in categories]


COLLECTIONS = [
    {
        "id": "minimal", "name": "Minimal", "subtitle": "Calm gradients & horizons", "icon": "filter_hdr",
        "emoji": "🏔️", "accent": "#F4A261",
        "pool": _scene_pool(_scenes_in("minimal"), 2) + _pattern_pool(["mesh_gradient", "grain_gradient", "layered_peaks", "silk_waves"], ALL_COLOURFUL),
    },
    {
        "id": "amoled", "name": "AMOLED", "subtitle": "True blacks, battery friendly", "icon": "dark_mode",
        "emoji": "🖤", "accent": "#8E8EA8",
        "pool": _pattern_pool(FEATURED_PATTERNS, DARK_PALETTES) + _scene_pool([s.value for s in SceneType if _scene_is_dark(s.value)]),
    },
    {
        "id": "cosmic", "name": "Cosmic", "subtitle": "Stars, planets & nebulae", "icon": "rocket_launch",
        "emoji": "🪐", "accent": "#9D8CFF",
        "pool": _scene_pool(_scenes_in("celestial") + ["ringed_planet", "aurora_lake", "moonlit_dunes"], 2) + _pattern_pool(_featured_in("cosmic") + ["bokeh"], DARK_PALETTES),
    },
    {
        "id": "nature", "name": "Nature", "subtitle": "Forests, peaks & oceans", "icon": "forest",
        "emoji": "🌲", "accent": "#6FCF97",
        "pool": _scene_pool(_scenes_in("nature_elements", "world_scenes") + ["misty_forest", "lone_tree", "minimal_mountains", "paper_hills", "ocean_sunset"]) + _pattern_pool(_featured_in("landscapes", "organic"), ALL_COLOURFUL),
    },
    {
        "id": "neon", "name": "Neon Nights", "subtitle": "Electric colour after dark", "icon": "bolt",
        "emoji": "⚡", "accent": "#FF2A6D",
        "pool": _scene_pool(["neon_city", "night_market", "rainy_street", "city_dusk", "bioluminescent", "subway"]) + _pattern_pool(_featured_in("tech", "cosmic", "geometric"), [p for p in VIVID_PALETTES if p in DARK_PALETTES] or VIVID_PALETTES),
    },
    {
        "id": "abstract", "name": "Abstract", "subtitle": "Shapes, flow & texture", "icon": "blur_on",
        "emoji": "🌀", "accent": "#7C8CFF",
        "pool": _pattern_pool(_featured_in("gradients", "geometric", "artistic", "organic"), ALL_COLOURFUL),
    },
    {
        "id": "pastel", "name": "Pastel", "subtitle": "Light, airy & soft", "icon": "palette",
        "emoji": "🌸", "accent": "#F6A6C8",
        "pool": _pattern_pool(FEATURED_PATTERNS, LIGHT_PALETTES) + _scene_pool(["paper_hills", "minimal_mountains", "misty_forest"]),
    },
    {
        "id": "landmarks", "name": "Landmarks", "subtitle": "Wonders of the world", "icon": "account_balance",
        "emoji": "🗼", "accent": "#FFB86B",
        "pool": _scene_pool(_scenes_in("landmarks")),
    },
    {
        "id": "dreamscapes", "name": "Dreamscapes", "subtitle": "Fantasy & the deep sea", "icon": "auto_fix_high",
        "emoji": "🏰", "accent": "#C38BFF",
        "pool": _scene_pool(_scenes_in("fantasy", "underwater")),
    },
]
COLLECTIONS_BY_ID = {c["id"]: c for c in COLLECTIONS}

# The default "For you" feed mixes everything that looks great.
DISCOVER_POOL = (
    _pattern_pool(FEATURED_PATTERNS, ALL_COLOURFUL)
    + _scene_pool([s.value for s in SceneType], 1)
)

# ----------------------------------------------------------------------------
# Items + feed
# ----------------------------------------------------------------------------


def _theme_name(theme_id):
    return SCENE_THEMES.get(theme_id, {}).get("name", theme_id.replace("_", " ").title())


def make_item(kind, key, palette, seed, inverted=False):
    palette = int(palette)
    if kind == "scene":
        definition = SCENE_DEFINITIONS[SceneType(key)]
        colors = definition["default_palette"] if palette < 0 else PALETTES[palette]["colors"]
        name = definition["name"]
        subtitle = _theme_name(definition["theme"].value) if palette < 0 else PALETTES[palette]["name"]
        category = definition["theme"].value
    else:
        palette = max(0, palette)
        colors = PALETTES[palette]["colors"]
        name = pattern_name(key)
        subtitle = PALETTES[palette]["name"]
        category = PATTERN_CATEGORY[key]
    return {
        "id": f"{kind}:{key}:{palette}:{seed}:{int(bool(inverted))}",
        "kind": kind,
        "key": key,
        "name": name,
        "subtitle": subtitle,
        "category": category,
        "palette": palette,
        "seed": int(seed),
        "inverted": bool(inverted),
        "colors": list(colors),
    }


def day_seed(now=None):
    now = now or datetime.now(timezone.utc)
    return int(now.strftime("%Y%m%d"))


def _weighted_choice(rng, pool):
    total = sum(t[3] for t in pool)
    pick = rng.uniform(0, total)
    for template in pool:
        pick -= template[3]
        if pick <= 0:
            return template
    return pool[-1]


def feed(collection=None, page=0, page_size=24, salt=None):
    """Deterministic, infinite curated feed (stable for a given day/salt)."""
    pool = COLLECTIONS_BY_ID[collection]["pool"] if collection else DISCOVER_POOL
    salt = day_seed() if salt is None else salt
    items, last_key = [], None
    for index in range(page * page_size, (page + 1) * page_size):
        rng = random.Random(f"{collection or 'discover'}:{salt}:{index}")
        for _ in range(4):  # avoid showing the same key twice in a row
            kind, key, palettes, _ = _weighted_choice(rng, pool)
            if key != last_key:
                break
        palette = rng.choice(palettes)
        items.append(make_item(kind, key, palette, rng.randint(100000, 999999)))
        last_key = key
    return items


def hero(salt=None, count=6):
    salt = day_seed() if salt is None else salt
    rng = random.Random(f"hero:{salt}")
    picks = rng.sample(list(PREMIUM_WEIGHT), 3) + rng.sample(_scenes_in("minimal"), 3)
    rng.shuffle(picks)
    out = []
    for key in picks[:count]:
        if key in PREMIUM_WEIGHT:
            out.append(make_item("pattern", key, rng.choice(ALL_COLOURFUL), rng.randint(100000, 999999)))
        else:
            out.append(make_item("scene", key, -1, rng.randint(100000, 999999)))
    return out


def catalog():
    salt = day_seed()
    patterns = [
        {"key": p.value, "name": pattern_name(p.value), "category": PATTERN_CATEGORY[p.value],
         "glyph": PATTERN_GLYPHS.get(p.value, "🎨"), "featured": p.value in FEATURED_PATTERNS}
        for p in PatternType
    ]
    themes = []
    for theme_id in THEME_ORDER:
        meta = SCENE_THEMES[theme_id]
        scenes = [
            {"key": s.value, "name": d["name"], "emoji": d["emoji"], "colors": d["default_palette"]}
            for s, d in SCENE_DEFINITIONS.items() if d["theme"].value == theme_id
        ]
        if scenes:
            themes.append({"id": theme_id, **meta, "scenes": scenes})
    collections = []
    for c in COLLECTIONS:
        cover = feed(c["id"], 0, 1, salt)[0]
        collections.append({k: c[k] for k in ("id", "name", "subtitle", "icon", "emoji", "accent")} | {"cover": cover})
    return {
        "version": 2,
        "day": salt,
        "sizes": {"mobile": [1290, 2796], "desktop": [3840, 2160]},
        "pattern_categories": [{k: c[k] for k in ("id", "name", "icon", "emoji", "accent", "description")} for c in PATTERN_CATEGORIES],
        "patterns": patterns,
        "scene_themes": themes,
        "palettes": PALETTES,
        "collections": collections,
        "hero": hero(salt),
    }
