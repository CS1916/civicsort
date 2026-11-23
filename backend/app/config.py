import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Smart Urban Waste Segregation & Intelligent Route Optimization API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # YOLO Computer Vision Config
    # If a trained custom weights file exists (e.g. weights/waste_yolov8.pt), use it,
    # otherwise fallback to yolov8n.pt or heuristic computer vision pipeline
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "weights/yolov8s.pt")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.45"))

    # OSRM Street Routing Server (Defaults to OpenStreetMap public OSRM, with automatic Haversine fallback)
    OSRM_BASE_URL: str = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")

    # Fleet & Environmental Metrics
    DIESEL_CONSUMPTION_L_PER_KM: float = 0.31   # Medium municipal refuse truck (liters/km)
    CO2_EMISSION_KG_PER_LITER: float = 2.65     # kg CO2 per liter of diesel
    AVERAGE_SPEED_KMH: float = 22.0             # Urban collection speed including traffic
    SERVICE_TIME_PER_BIN_MINS: int = 4          # Loading & compaction time per bin

    # CORS origins
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "*"
    ]

settings = Settings()
