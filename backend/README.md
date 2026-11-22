# Urban Waste Management Backend API

FastAPI backend powering Computer Vision Waste Segregation (Ultralytics YOLO) and Vehicle Routing Problem solver (Google OR-Tools + OSRM street network).

## Quick Start (Local Development)

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger documentation available at: `http://localhost:8000/docs`

## API Endpoints Summary

- `GET /`: Health & system metadata
- `GET /health`: Operational status & active models
- `POST /api/classify-waste`: Accepts image upload or base64 data string; runs YOLO detection and returns bin color code (Blue/Green/Red) and disposal instructions.
- `POST /api/optimize-route`: Computes standard naive sweep vs AI smart route (only bins with fill level >= 75%) and returns distance/time/fuel/CO2 savings.
- `GET /api/bins`: Returns current IoT telemetry smart bins in the urban grid.
- `GET /api/analytics`: Returns 7-day historical benchmarks and material breakdown.
