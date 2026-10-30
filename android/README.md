# WallBloom Android app

Native Kotlin + Jetpack Compose Android client for the FastAPI wallpaper generator. The React frontend is removed from this project.

## Requirements

- Android Studio Hedgehog or newer
- JDK 17
- Android SDK Platform 35 and Build Tools 35.x
- Python 3.9+ for the backend

## Configure the backend

Edit one line in `android/gradle.properties`:

```properties
API_BASE_URL=https://wallbloom.onrender.com
```

The default value is the verified production API. For local development, change it to:

```properties
# Android emulator -> host computer
API_BASE_URL=http://10.0.2.2:8000

# Physical Android device -> computer LAN address
API_BASE_URL=http://192.168.1.25:8000
```

You can also override the same property without editing the file:

```bash
./gradlew assembleDebug -PAPI_BASE_URL=http://10.0.2.2:8000
./gradlew bundleRelease -PAPI_BASE_URL=https://wallbloom.onrender.com
```

The app uses `BuildConfig.API_BASE_URL` for health/data requests, preview images, and PNG downloads. No login or user account is required.

## Run the backend locally

```bash
cd ../backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Verify the API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/patterns
```

## Build and install

From this `android` directory:

```bash
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
./gradlew bundleRelease
```

Outputs:

- Debug APK: `android/app/build/outputs/apk/debug/app-debug.apk`
- Release AAB: `android/app/build/outputs/bundle/release/app-release.aab`

The release bundle is unsigned by default. Add a private signing configuration before uploading to Google Play.

## UI features

- Branded WallBloom adaptive launcher icon
- Patterns and themed scenes loaded from the FastAPI API
- Web-matched emoji pattern icons for the full WallBloom catalog
- First 40 patterns shown with a View more expansion, matching the web app
- Independently scrollable blend-pattern picker
- Scene cards with category and emoji labels
- Palette cards with actual server-provided color swatches
- Desktop 16:9 and mobile 9:19.5 live previews
- Pattern blending with adjustable strength
- Palette inversion beside Color direction and deterministic shuffle
- Preview cards with view icons and icon-only PNG download actions
- Images saved into `Pictures/WallBloom`
- Clear connection and download error messages

## API catalog and debug inspection

The app loads the complete catalog from the production API: all pattern records from `/api/patterns` and all palette records from `/api/palettes`. The Android screen renders them as full grids. Selecting a pattern changes the preview request's `pattern_type`; selecting a palette changes `palette_index`.

Debug builds use Chucker 4.1.0 to inspect OkHttp requests. Install the debug APK, open the Chucker notification or Chucker app entry, and inspect API calls to `https://wallbloom.onrender.com`. Release builds use Chucker's no-op artifact.

## Health-gated startup

At launch, WallBloom calls `GET https://wallbloom.onrender.com/health` before loading the editor. The splash screen remains visible and retries until HTTP 200 plus the initial catalogs are available. Every `ON_START` lifecycle event, including returning from background, runs the health check again. A transient foreground failure keeps the last loaded editor state visible.
