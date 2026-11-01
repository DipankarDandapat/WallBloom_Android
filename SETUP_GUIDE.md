# WallBloom setup guide

The project now has two parts: a Python FastAPI backend and a native Kotlin Android app. The React frontend has been removed.

See `android/README.md` for the complete Android Studio, Gradle, URL configuration, emulator/physical-device, APK, and AAB instructions.

Backend quick start:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   // .venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

Health check:

```bash
curl http://localhost:8000/health
```
