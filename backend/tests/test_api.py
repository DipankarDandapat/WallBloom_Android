"""API + engine tests. Run from backend/: `python -m pytest -q`."""

import io
import os
import sys

import pytest
from PIL import Image

os.environ["WARM_CACHE"] = "0"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

import catalog  # noqa: E402
from main import app  # noqa: E402
from pattern_engine import PRESET_PALETTES, PatternType  # noqa: E402
from scene_engine import SCENE_DEFINITIONS, SceneType  # noqa: E402

client = TestClient(app)


def _image(response):
    return Image.open(io.BytesIO(response.content))


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"


def test_catalog_shape():
    data = client.get("/api/v2/catalog").json()
    assert data["version"] == 2
    assert len(data["patterns"]) == len(PatternType)
    assert len(data["palettes"]) == len(PRESET_PALETTES)
    assert sum(len(t["scenes"]) for t in data["scene_themes"]) == len(SceneType)
    for collection in data["collections"]:
        assert collection["icon"] and collection["accent"].startswith("#")
        assert collection["cover"]["kind"] in ("pattern", "scene")
    assert len(data["hero"]) == 6


def test_every_pattern_is_categorised_and_every_scene_has_a_theme():
    categories = {c["id"] for c in catalog.PATTERN_CATEGORIES}
    assert all(catalog.PATTERN_CATEGORY[p.value] in categories for p in PatternType)
    assert all(d["theme"].value in catalog.SCENE_THEMES for d in SCENE_DEFINITIONS.values())


def test_feed_is_deterministic_and_paginates():
    a = client.get("/api/v2/feed", params={"page": 0, "salt": 7}).json()["items"]
    b = client.get("/api/v2/feed", params={"page": 0, "salt": 7}).json()["items"]
    c = client.get("/api/v2/feed", params={"page": 1, "salt": 7}).json()["items"]
    assert a == b and a != c and len(a) == 24
    assert all(x["key"] != y["key"] for x, y in zip(a, a[1:]))


@pytest.mark.parametrize("collection", [c["id"] for c in catalog.COLLECTIONS])
def test_collection_feeds(collection):
    items = client.get("/api/v2/feed", params={"collection": collection, "page_size": 10}).json()["items"]
    assert len(items) == 10


def test_unknown_collection_404():
    assert client.get("/api/v2/feed", params={"collection": "nope"}).status_code == 404


def test_render_thumb_and_cache_headers():
    params = {"kind": "pattern", "key": "mesh_gradient", "palette": 3, "seed": 1, "w": 270, "h": 585, "quality": "thumb"}
    r = client.get("/api/v2/render", params=params)
    assert r.status_code == 200 and r.headers["content-type"] == "image/webp"
    assert "immutable" in r.headers["cache-control"]
    assert _image(r).size == (270, 585)
    r2 = client.get("/api/v2/render", params=params, headers={"If-None-Match": r.headers["etag"]})
    assert r2.status_code == 304


def test_render_device_aspect_scene_png_download():
    r = client.get("/api/v2/render", params={"kind": "scene", "key": "ocean_sunset", "w": 1080, "h": 2400,
                                             "fmt": "png", "download": True})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert "attachment" in r.headers["content-disposition"]
    assert _image(r).size == (1080, 2400)


def test_render_desktop_4k():
    r = client.get("/api/v2/render", params={"kind": "scene", "key": "city_dusk", "w": 3840, "h": 2160, "fmt": "jpeg"})
    assert r.status_code == 200 and _image(r).size == (3840, 2160)


def test_full_quality_preview_matches_download_pixels():
    base = {"kind": "pattern", "key": "contour", "palette": 5, "seed": 99, "fmt": "png"}
    full = _image(client.get("/api/v2/render", params=base | {"w": 1290, "h": 2796}))
    v1 = _image(client.get("/api/wallpapers/download/mobile",
                           params={"pattern_type": "contour", "palette_index": 5, "seed": 99}))
    assert full.tobytes() == v1.tobytes()


@pytest.mark.parametrize("params", [
    {"kind": "pattern", "key": "nope"},
    {"kind": "scene", "key": "nope"},
    {"kind": "pattern", "key": "waves", "palette": 9999},
    {"kind": "pattern", "key": "waves", "w": 100000, "h": 10},
    {"kind": "pattern", "key": "waves", "fmt": "gif"},
])
def test_render_validation(params):
    assert client.get("/api/v2/render", params=params).status_code == 400


def test_v1_errors_are_real_http_errors():
    r = client.get("/api/wallpapers/preview", params={"pattern_type": "does_not_exist"})
    assert r.status_code == 400


def test_v1_endpoints_still_work():
    assert len(client.get("/api/patterns").json()["patterns"]) == len(PatternType)
    assert len(client.get("/api/palettes").json()) == len(PRESET_PALETTES)
    themes = client.get("/api/scenes").json()["themes"]
    assert any(t["id"] == "minimal" for t in themes)
    r = client.get("/api/wallpapers/scene", params={"scene_type": "aurora_lake", "width": 390, "height": 844})
    assert r.status_code == 200 and _image(r).size == (390, 844)


def test_scene_inversion_applies_to_default_palette():
    base = {"kind": "scene", "key": "lone_tree", "seed": 3, "w": 200, "h": 400, "fmt": "png"}
    normal = _image(client.get("/api/v2/render", params=base)).tobytes()
    inverted = _image(client.get("/api/v2/render", params=base | {"inverted": True})).tobytes()
    assert normal != inverted


@pytest.mark.parametrize("key", [p.value for p in PatternType])
def test_every_pattern_renders(key):
    r = client.get("/api/v2/render", params={"kind": "pattern", "key": key, "palette": 60, "w": 120, "h": 260,
                                             "quality": "thumb"})
    assert r.status_code == 200


@pytest.mark.parametrize("key", [s.value for s in SceneType])
def test_every_scene_renders(key):
    r = client.get("/api/v2/render", params={"kind": "scene", "key": key, "w": 120, "h": 260, "quality": "thumb"})
    assert r.status_code == 200
