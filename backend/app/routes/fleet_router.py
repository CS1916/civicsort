from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import (
    list_vehicles,
    get_vehicle,
    create_vehicle,
    update_vehicle,
    list_drivers,
    create_driver,
    update_driver,
)

router = APIRouter(prefix="", tags=["Fleet & Driver Management"])


class CreateVehiclePayload(BaseModel):
    name: str
    model: str
    plate_number: str
    status: str = "Available"
    driver_id: Optional[str] = None
    fuel_battery_pct: int = 100
    capacity_tons: float = 5.0
    current_lat: float = 12.9756
    current_lng: float = 77.6097
    assigned_zone: str = "Central Core"


class UpdateVehiclePayload(BaseModel):
    status: Optional[str] = None
    driver_id: Optional[str] = None
    fuel_battery_pct: Optional[int] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    assigned_zone: Optional[str] = None


class CreateDriverPayload(BaseModel):
    name: str
    phone: str
    license_no: str
    status: str = "On Duty"
    rating: float = 4.8
    assigned_vehicle_id: Optional[str] = None


class UpdateDriverPayload(BaseModel):
    status: Optional[str] = None
    phone: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None
    rating: Optional[float] = None


# --- VEHICLES ENDPOINTS ---
@router.get("/vehicles")
@router.get("/api/vehicles")
async def get_vehicles():
    """Lists all municipal collection trucks with driver assignments and battery status."""
    return list_vehicles()


@router.post("/vehicles")
@router.post("/api/vehicles")
async def add_vehicle(payload: CreateVehiclePayload):
    """Registers a new vehicle in the municipal fleet."""
    veh = create_vehicle(payload.dict())
    return {"success": True, "vehicle": veh}


@router.put("/vehicles/{veh_id}")
@router.put("/api/vehicles/{veh_id}")
async def modify_vehicle(veh_id: str, payload: UpdateVehiclePayload):
    """Updates vehicle status, driver assignment, or battery level."""
    updated = update_vehicle(veh_id, {k: v for k, v in payload.dict().items() if v is not None})
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    return {"success": True, "vehicle": updated}


# --- DRIVERS ENDPOINTS ---
@router.get("/drivers")
@router.get("/api/drivers")
async def get_drivers():
    """Lists all licensed municipal drivers."""
    return list_drivers()


@router.post("/drivers")
@router.post("/api/drivers")
async def add_driver(payload: CreateDriverPayload):
    """Enrolls a new municipal driver."""
    drv = create_driver(payload.dict())
    return {"success": True, "driver": drv}


@router.put("/drivers/{driver_id}")
@router.put("/api/drivers/{driver_id}")
async def modify_driver(driver_id: str, payload: UpdateDriverPayload):
    """Updates driver status, phone, or assigned vehicle."""
    updated = update_driver(driver_id, {k: v for k, v in payload.dict().items() if v is not None})
    if not updated:
        raise HTTPException(status_code=404, detail="Driver not found.")
    return {"success": True, "driver": updated}
