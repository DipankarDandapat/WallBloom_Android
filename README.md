# WallBloom — FastAPI backend + native Android app

WallBloom is a stateless procedural wallpaper generator. This distribution contains the Python FastAPI image engine and a native Kotlin/Jetpack Compose Android client. The React frontend and its `node_modules` have been removed.

## Project structure

```text
aurawall/
├── backend/       # FastAPI + Pillow pattern and scene generation
├── android/       # Kotlin/Compose Android application
├── artifacts/     # Verified debug APK and release AAB
├── doc/           # Original design reference
└── SETUP_GUIDE.md
```

Start with [`android/README.md`](android/README.md) for Android setup, one-line API configuration, emulator/physical-device networking, APK generation, and AAB generation.

## Quick start

Terminal 1 — backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Terminal 2 — Android:

```bash
cd android
./gradlew assembleDebug
./gradlew bundleRelease
```

The default `android/gradle.properties` value is:

```properties
API_BASE_URL=https://wallbloom.onrender.com
```

For local development, change only that line to `http://10.0.2.2:8000` for an Android emulator or your computer LAN IP for a physical device. The same URL drives data loading, previews, and downloads.

The Android UI includes branded launcher icons, visual pattern cards with type-based glyphs, scene cards, actual API palette swatches, dual previews, blending, inversion, shuffle, and clean PNG export. The app is open access: there is no login, account, database, or user flow. Preview and download requests use the same pattern, palette, seed, inversion, blend, scene, and resolution parameters, so the downloaded image is deterministic and matches the selected configuration.
