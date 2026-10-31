# WallBloom Android app

Native Kotlin + Jetpack Compose client for the WallBloom FastAPI renderer.

## Requirements

- Android Studio (Ladybug or newer) or the command-line SDK
- JDK 17
- Android SDK Platform 35
- minSdk 26 (Android 8.0), targetSdk 35

## Configure the backend

`android/gradle.properties`:

```properties
API_BASE_URL=https://wallbloom.onrender.com
```

Override per build without editing the file:

```bash
./gradlew assembleDebug -PAPI_BASE_URL=http://10.0.2.2:8000      # emulator -> host machine
./gradlew assembleDebug -PAPI_BASE_URL=http://192.168.1.25:8000  # physical device -> LAN IP
```

Plain `http://` is allowed in **debug builds only** (`src/debug/AndroidManifest.xml`). Release builds require HTTPS.

## Build, test, install

```bash
./gradlew testDebugUnitTest        # JVM tests: JSON parsing, URL building, v1 fallback, repository caching
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
./gradlew assembleRelease bundleRelease   # R8-minified and resource-shrunk (~1.9 MB APK)
```

Release artifacts are unsigned. Add a private signing config before uploading to Google Play; never commit keystores.

## Architecture

```text
com.aurawall.app
├── WallBloomApplication   manual DI container, shared OkHttp client, Coil image loader (300 MB disk cache)
├── MainActivity           splash screen, edge-to-edge, theme
├── data/                  models, JSON mapping, API client, v2/v1 image URL builders,
│                          repository (disk-cached catalog, v1 fallback), DataStore prefs
├── system/DeviceActions   WallpaperManager (home/lock/both), MediaStore saving (+ API 26–28 path), share sheet
└── ui/
    ├── AppViewModel       catalog, paged feeds, favourites, studio and preview state, device actions
    ├── WallBloomApp       navigation, shared-element transitions, floating nav bar, toasts
    ├── components/        cards, shimmer, chips, server-driven icons (IconRegistry), buttons
    └── screens/           Discover, Collection, Scenes, Studio, Saved, Search, Settings, Preview
```

### Data flow

1. On launch the repository shows the catalog cached on disk (instant start, works offline), then refreshes `/api/v2/catalog` in the background. Free-tier hosts that are asleep get retries with a friendly "waking up" banner.
2. If `/api/v2/catalog` returns 404, the app switches to the v1 endpoints (`/api/patterns`, `/api/palettes`, `/api/scenes`) and builds the catalog and feed on the device.
3. Grids request fixed-size `quality=thumb` WebP renders (540×1170 phone, 960×540 desktop) so caches stay hot. The preview loads a `quality=full` render and shows the cached thumbnail until it arrives.

### Wallpaper actions

| | Phone wallpaper | Desktop wallpaper |
|---|---|---|
| Preview (zoom, lock/home mockups) | ✅ | ✅ (16:9, zoomable) |
| Set as Home / Lock / Both | ✅ rendered at the device's exact screen size | — |
| Download | 1290×2796 PNG → `Pictures/WallBloom` | 3840×2160 PNG → `Pictures/WallBloom` |
| Share | ✅ | ✅ |

`SET_WALLPAPER` is a normal (auto-granted) permission. `WRITE_EXTERNAL_STORAGE` is declared with `maxSdkVersion=28` and requested at runtime only on Android 8–9.

## Debugging

Debug builds include Chucker for inspecting HTTP calls (notification → Chucker). Release builds use the no-op artifact.
