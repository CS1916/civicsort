from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class WasteCategory(str, Enum):
    ORGANIC = "organic"
    RECYCLABLE = "recyclable"
    HAZARDOUS = "hazardous"
    GENERAL = "general"

class BoundingBox(BaseModel):
    x: float = Field(..., description="Top-left X coordinate percentage (0-100)")
    y: float = Field(..., description="Top-left Y coordinate percentage (0-100)")
    width: float = Field(..., description="Width percentage (0-100)")
    height: float = Field(..., description="Height percentage (0-100)")

class WasteDetection(BaseModel):
    id: str
    label: str
    category: WasteCategory
    confidence: float
    binName: str
    binColor: str  # "green", "blue", "red", "gray"
    disposalInstruction: str
    ecoTip: str
    bbox: Optional[BoundingBox] = None

class ClassifyResponse(BaseModel):
    success: bool
    item: WasteDetection
    alternativeDetections: Optional[List[WasteDetection]] = []
    processingTimeMs: float
    timestamp: str

class SmartBin(BaseModel):
    id: str
    code: str
    name: str
    address: str
    lat: float
    lng: float
    fillLevel: float = Field(..., ge=0, le=100)
    category: WasteCategory
    capacityKg: float = 100.0
    lastUpdated: str = "Just now"
    needsPickup: bool = False

class DepotLocation(BaseModel):
    id: str = "depot-01"
    name: str = "Central Eco-Hub & Fleet Depot"
    address: str = "Sanitation Logistics Sector 4, Civic Core"
    lat: float = 40.7128
    lng: float = -74.0060

class RoutePoint(BaseModel):
    lat: float
    lng: float
    binId: Optional[str] = None
    name: Optional[str] = None
    isDepot: bool = False
    order: int
    fillLevel: Optional[float] = None

class RouteStats(BaseModel):
    totalDistanceKm: float
    estimatedTimeMins: int
    fuelConsumedLiters: float
    co2EmittedKg: float
    binsVisited: int
    totalBinsAvailable: int

class RouteSavings(BaseModel):
    distanceSavedKm: float
    distanceSavedPercent: float
    timeSavedMins: int
    timeSavedPercent: float
    fuelSavedLiters: float
    co2SavedKg: float

class RouteBreakdown(BaseModel):
    points: List[RoutePoint]
    stats: RouteStats

class OptimizeRouteRequest(BaseModel):
    bins: List[SmartBin]
    depot: Optional[DepotLocation] = None
    fillThreshold: Optional[float] = 75.0

class OptimizeRouteResponse(BaseModel):
    depot: DepotLocation
    standardRoute: RouteBreakdown
    aiSmartRoute: RouteBreakdown
    savings: RouteSavings
    lastCalculated: str
