# WallBloom — procedural wallpapers for Android

WallBloom is a stateless procedural wallpaper generator: a Python FastAPI image engine plus a native Kotlin/Jetpack Compose Android app. Every wallpaper is generated from its parameters (generator, palette, seed), so the same parameters always produce the same pixels at any resolution.

## What's inside

| | |
|---|---|
| **107 generators** | 98 original procedural patterns + 9 premium generators (mesh gradient, grain gradient, layered peaks, silk waves, bokeh, liquid, flow lines, glass orbs, halftone) |
| **83 scenes** | 8 themes including the new **Minimal** theme (Alpine Haze, Misty Pines, Ocean Sunset, Moonlit Dunes, Ringed Planet, Aurora Lake, Lone Tree, Paper Hills, City at Dusk) |
| **70 palettes** | 50 originals + 20 curated palettes (Midnight Bloom, Nordic Frost, Cyberpunk, AMOLED Violet…), auto-tagged dark/AMOLED/light/vivid |
| **9 collections** | Minimal, AMOLED, Cosmic, Nature, Neon Nights, Abstract, Pastel, Landmarks, Dreamscapes |

## App highlights

- **Discover**: daily featured carousel, server-driven collections and an infinite curated feed with pull-to-refresh.
- **Scenes**: every illustrated scene grouped by theme, with real rendered thumbnails.
- **Studio**: build your own wallpaper (generator, palette, invert, blend two patterns, seed).
- **Saved**: favourites stored on the device (long-press any card or tap the heart).
- **Full-screen preview**: swipe between wallpapers, pinch or double-tap to zoom, and preview over a lock-screen clock or home-screen icons. Recolour with any palette or shuffle the seed.
- **Phone wallpapers**: *Set wallpaper* on the **Home screen**, the **Lock screen**, or **Both**, rendered pixel-perfect for the device's resolution. Download (1290×2796 PNG) and share.
- **Desktop wallpapers**: preview and **download in 4K** (3840×2160 PNG) and share. Desktop wallpapers can't be applied on the phone.
- Shared-element transitions from card to preview, a floating animated nav bar, shimmer placeholders tinted with each wallpaper's palette, and light/dark/AMOLED themes.
- Categories, collections, icons and accent colours come from the API (`/api/v2/catalog`), so content changes without an app release.

## Project structure

```text
backend/   FastAPI + Pillow/numpy generators, render cache, v2 catalog/feed API, pytest suite
android/   Kotlin + Jetpack Compose app (data / system / ui layers), JVM unit tests
artifacts/ Previously published builds (v1.0, not rebuilt for v2)
doc/       Original design reference
```

## Quick start

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q        # 216 tests
python main.py             # http://localhost:8000/docs
```

Android (emulator against the local backend):

```bash
cd android
./gradlew testDebugUnitTest
./gradlew assembleDebug -PAPI_BASE_URL=http://10.0.2.2:8000
```

See [`android/README.md`](android/README.md) and [`backend/README.md`](backend/README.md) for details, and [`DEPLOYMENT.md`](DEPLOYMENT.md) for production.

## Compatibility

The app talks to the v2 API. If it reaches a backend that hasn't been upgraded yet (`/api/v2/catalog` returns 404), it switches to the original v1 endpoints automatically, so a new app build keeps working against an old server. Deploy the new backend to get the faster thumbnails, the curated feed and the new content.
