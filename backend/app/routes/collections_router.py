from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import list_collection_logs, create_collection_log

router = APIRouter(prefix="", tags=["Collection History & Logs"])


class DispatchCollectionPayload(BaseModel):
    vehicle_code: str = "TRK-01"
    driver_name: str = "Suresh Gowda"
    bins_serviced_count: int = 5
    total_weight_tons: float = 4.2
    distance_km: float = 23.8
    fuel_saved_liters: float = 7.6
    co2_avoided_kg: float = 20.1
    vehicle_id: Optional[str] = None


@router.get("/collections/history")
@router.get("/api/collections/history")
async def get_collection_history():
    """Returns historical collection runs with fuel saved and tonnage."""
    return list_collection_logs()


@router.post("/collections/dispatch")
@router.post("/api/collections/dispatch")
async def dispatch_collection(payload: DispatchCollectionPayload):
    """Logs an AI-optimized route dispatch and notifies the fleet."""
    entry = create_collection_log(payload.dict())
    return {"success": True, "collectionRun": entry}
