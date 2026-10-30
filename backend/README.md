# WallBloom Backend - FastAPI

Simple, stateless FastAPI backend for wallpaper generation. No authentication, no database required.

## Features

✅ **10 Procedural Patterns**
- Hills, Waves, Dunes, Mountains, Arcs, Scribble, Geometric, Noise, Gradient, Cellular

✅ **12 Color Palettes**
- Charcoal, Stone, Ocean Blue, Sunrise, Fire, Purple, Neon, Arctic, Forest, Sunset, Deep Space, Tropical

✅ **Deterministic Generation**
- Same seed + pattern + palette = same image every time
- Perfect for reproducibility

✅ **High-Resolution Exports**
- Desktop: 3840x2160 (4K)
- Mobile: 1290x2796

✅ **No Authentication**
- Open access to all endpoints
- No database required
- Stateless design

## Installation

### Prerequisites
- Python 3.9+
- pip or pip3

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Backend

```bash
python main.py
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## API Endpoints

### Health Check
```bash
GET /health
```

### List Patterns
```bash
GET /api/patterns
```

Response:
```json
{
  "patterns": [
    {"type": "hills", "name": "Hills", "description": "A hills pattern"}
  ]
}
```

### List Palettes
```bash
GET /api/palettes
```

Response:
```json
[
  {
    "id": 0,
    "name": "Charcoal",
    "colors": ["#1a1a1a", "#4a4a4a", "#8a8a8a", "#d0d0d0"],
    "description": "Palette: Charcoal",
    "is_preset": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### Generate Wallpaper (Metadata Only)
```bash
POST /api/wallpapers/generate
Content-Type: application/json

{
  "pattern_type": "hills",
  "palette_index": 0,
  "seed": 12345,
  "inverted": false
}
```

Response:
```json
{
  "id": 12345,
  "pattern_type": "hills",
  "palette_index": 0,
  "seed": 12345,
  "inverted": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Get Preview Image
```bash
GET /api/wallpapers/preview?pattern_type=hills&palette_index=0&seed=12345&inverted=false&width=800&height=600
```

Returns: PNG image (800x600)

### Download Desktop Wallpaper (4K)
```bash
GET /api/wallpapers/download/desktop?pattern_type=hills&palette_index=0&seed=12345&inverted=false
```

Returns: PNG file (3840x2160)

### Download Mobile Wallpaper
```bash
GET /api/wallpapers/download/mobile?pattern_type=hills&palette_index=0&seed=12345&inverted=false
```

Returns: PNG file (1290x2796)

## Usage Examples

### cURL

```bash
# Get patterns
curl http://localhost:8000/api/patterns

# Get palettes
curl http://localhost:8000/api/palettes

# Get preview
curl "http://localhost:8000/api/wallpapers/preview?pattern_type=hills&palette_index=0&seed=12345" > preview.png

# Download desktop
curl "http://localhost:8000/api/wallpapers/download/desktop?pattern_type=hills&palette_index=0&seed=12345" > wallpaper_desktop.png

# Download mobile
curl "http://localhost:8000/api/wallpapers/download/mobile?pattern_type=hills&palette_index=0&seed=12345" > wallpaper_mobile.png
```

### Python

```python
import requests

# Get preview
response = requests.get(
    "http://localhost:8000/api/wallpapers/preview",
    params={
        "pattern_type": "hills",
        "palette_index": 0,
        "seed": 12345,
        "width": 800,
        "height": 600
    }
)
with open("preview.png", "wb") as f:
    f.write(response.content)

# Download desktop
response = requests.get(
    "http://localhost:8000/api/wallpapers/download/desktop",
    params={
        "pattern_type": "hills",
        "palette_index": 0,
        "seed": 12345
    }
)
with open("wallpaper.png", "wb") as f:
    f.write(response.content)
```

### JavaScript/Fetch

```javascript
// Get preview
fetch('http://localhost:8000/api/wallpapers/preview?pattern_type=hills&palette_index=0&seed=12345')
  .then(r => r.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);
  });

// Download desktop
fetch('http://localhost:8000/api/wallpapers/download/desktop?pattern_type=hills&palette_index=0&seed=12345')
  .then(r => r.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'wallpaper.png';
    a.click();
  });
```

## API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

### Pattern Generation
- **Seeded Random**: Uses Python's `random.Random(seed)` for reproducibility
- **PIL/Pillow**: Image generation and drawing
- **Deterministic**: Same parameters always produce same image

### Patterns
Each pattern generates unique visuals:
- **Hills**: Sine wave based hills
- **Waves**: Layered wave pattern
- **Dunes**: Sand dune simulation
- **Mountains**: Peak-based mountains
- **Arcs**: Circular arc pattern
- **Scribble**: Random line pattern
- **Geometric**: Shapes (circles, rectangles, triangles)
- **Noise**: Random colored squares
- **Gradient**: Linear color gradient
- **Cellular**: Grid-based cellular pattern

### Color Palettes
12 preset palettes with 4 colors each:
- Charcoal, Stone, Ocean Blue, Sunrise, Fire, Purple
- Neon, Arctic, Forest, Sunset, Deep Space, Tropical

### Image Export
- **PNG Format**: Lossless compression
- **Resolutions**:
  - Desktop: 3840x2160 (4K)
  - Mobile: 1290x2796
  - Preview: Custom size

## Performance

### Generation Times (Approximate)
- Preview (800x600): 50-100ms
- Desktop (3840x2160): 500-1000ms
- Mobile (1290x2796): 300-600ms

### Memory Usage
- Preview: ~2-5 MB
- Desktop: ~20-30 MB
- Mobile: ~15-20 MB

## Troubleshooting

### Port 8000 Already in Use
```bash
# Use different port
PORT=8001 python main.py

# Or kill existing process
lsof -i :8000
kill -9 <PID>
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### Image Generation Errors
- Check pattern_type is valid
- Check palette_index is 0-11
- Check seed is positive integer

## Development

### Run with Auto-Reload
```bash
python main.py
```

### Format Code
```bash
pip install black
black main.py pattern_engine.py
```

### Type Checking
```bash
pip install mypy
mypy main.py pattern_engine.py
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
docker build -t aurawall-backend .
docker run -p 8000:8000 aurawall-backend
```

### Gunicorn (Production)
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Cloud Platforms
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **Render**: Connect GitHub repo
- **AWS**: Elastic Beanstalk, Lambda
- **Google Cloud**: Cloud Run
