# WallBloom deployment guide

WallBloom now ships as a Python FastAPI backend plus a native Kotlin/Jetpack Compose Android app. The React frontend and its Node modules are not part of this distribution.

## Deploy the FastAPI backend

The backend is stateless and requires no database or authentication:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PORT=8000 python main.py
```

Deploy `backend/` to any Python-compatible service such as Render, Railway, Fly.io, or a VM. Set the service start command to `python main.py` and expose the configured `PORT`. Verify:

```bash
curl https://your-api.example.com/health
```

## Build the Android app against production

Edit the single API property in `android/gradle.properties`:

```properties
API_BASE_URL=https://your-api.example.com
```

Then build the unsigned release bundle:

```bash
cd android
./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`.

For a one-off URL override:

```bash
./gradlew bundleRelease -PAPI_BASE_URL=https://your-api.example.com
```

The release bundle is unsigned by default. Configure a private signing key in `android/app/build.gradle.kts` before uploading to Google Play. Never commit a keystore or passwords.

## Local development

- Android emulator: use `http://10.0.2.2:8000`.
- Physical Android device: use the development machine LAN address, for example `http://192.168.1.25:8000`.
- Set the value as `API_BASE_URL` in `android/gradle.properties`, or pass `-PAPI_BASE_URL=...` to `assembleDebug`.
- The manifest allows cleartext HTTP for local development. Use HTTPS for production.
