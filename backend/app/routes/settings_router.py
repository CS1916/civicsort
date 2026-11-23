import os
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="", tags=["System Settings & Map Configuration"])

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map_settings.json")

class MapKeyPayload(BaseModel):
    provider: str = "esri"  # "esri", "maptiler", "mapbox", "google"
    apiKey: Optional[str] = ""
    imageryStyle: Optional[str] = "hybrid"  # "satellite", "hybrid", "street"

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "provider": "esri",
        "apiKey": "",
        "imageryStyle": "hybrid",
        "defaultFallback": "Esri World Imagery + Labels (Free, zero-watermark, 100% active)"
    }

def save_settings(data: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.get("/settings/map-key")
async def get_map_key():
    """Returns the current map provider and API key configuration."""
    return load_settings()

@router.post("/settings/map-key")
async def update_map_key(payload: MapKeyPayload):
    """Updates and persists the custom map API key configuration."""
    data = load_settings()
    data["provider"] = payload.provider
    data["apiKey"] = payload.apiKey or ""
    data["imageryStyle"] = payload.imageryStyle or "hybrid"
    data["lastUpdated"] = "Just now"
    save_settings(data)
    return {
        "success": True,
        "message": "Map API Key configuration saved successfully.",
        "settings": data
    }
