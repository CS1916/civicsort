from fastapi import APIRouter
from typing import List, Dict, Any
from app.models.schemas import SmartBin, WasteCategory

router = APIRouter(prefix="", tags=["IoT Smart Bins & Telemetry"])

# Initial city bins database state
DEMO_BINS: List[SmartBin] = [
    SmartBin(id="bin-101", code="BIN-101", name="Metro Station Gate 2", address="Broadway & 14th St", lat=40.7359, lng=-73.9911, fillLevel=88.0, category=WasteCategory.RECYCLABLE, capacityKg=120.0, lastUpdated="4 mins ago", needsPickup=True),
    SmartBin(id="bin-102", code="BIN-102", name="Civic Park Promenade", address="5th Ave & Central Path", lat=40.7651, lng=-73.9740, fillLevel=25.0, category=WasteCategory.ORGANIC, capacityKg=80.0, lastUpdated="12 mins ago", needsPickup=False),
    SmartBin(id="bin-103", code="BIN-103", name="Green Market Plaza", address="Union Sq West & 16th St", lat=40.7368, lng=-73.9902, fillLevel=94.0, category=WasteCategory.ORGANIC, capacityKg=150.0, lastUpdated="2 mins ago", needsPickup=True),
    SmartBin(id="bin-104", code="BIN-104", name="Tech Park Tower B", address="Hudson Yards South", lat=40.7538, lng=-74.0022, fillLevel=45.0, category=WasteCategory.RECYCLABLE, capacityKg=120.0, lastUpdated="18 mins ago", needsPickup=False),
    SmartBin(id="bin-105", code="BIN-105", name="City Hospital East Wing", address="1st Ave & 34th St", lat=40.7441, lng=-73.9742, fillLevel=82.0, category=WasteCategory.HAZARDOUS, capacityKg=100.0, lastUpdated="7 mins ago", needsPickup=True),
    SmartBin(id="bin-106", code="BIN-106", name="University Library Lawn", address="Washington Sq South", lat=40.7298, lng=-73.9972, fillLevel=18.0, category=WasteCategory.RECYCLABLE, capacityKg=100.0, lastUpdated="25 mins ago", needsPickup=False),
    SmartBin(id="bin-107", code="BIN-107", name="High Street Shopping Arcade", address="5th Ave & 42nd St", lat=40.7527, lng=-73.9818, fillLevel=96.0, category=WasteCategory.RECYCLABLE, capacityKg=160.0, lastUpdated="1 min ago", needsPickup=True),
    SmartBin(id="bin-108", code="BIN-108", name="Residential Block C", address="Greenwich St & Perry St", lat=40.7342, lng=-74.0075, fillLevel=62.0, category=WasteCategory.GENERAL, capacityKg=110.0, lastUpdated="15 mins ago", needsPickup=False),
    SmartBin(id="bin-109", code="BIN-109", name="Waterfront Food Court", address="Battery Park Esplanade", lat=40.7058, lng=-74.0169, fillLevel=79.0, category=WasteCategory.ORGANIC, capacityKg=140.0, lastUpdated="8 mins ago", needsPickup=True),
    SmartBin(id="bin-110", code="BIN-110", name="Railway Terminal South", address="Penn Station Plaza", lat=40.7505, lng=-73.9934, fillLevel=85.0, category=WasteCategory.RECYCLABLE, capacityKg=150.0, lastUpdated="6 mins ago", needsPickup=True),
    SmartBin(id="bin-111", code="BIN-111", name="Financial District North", address="Wall St & William St", lat=40.7069, lng=-74.0089, fillLevel=32.0, category=WasteCategory.RECYCLABLE, capacityKg=90.0, lastUpdated="30 mins ago", needsPickup=False),
    SmartBin(id="bin-112", code="BIN-112", name="Botanical Garden Entry", address="FDR Drive Riverwalk", lat=40.7180, lng=-73.9780, fillLevel=38.0, category=WasteCategory.ORGANIC, capacityKg=85.0, lastUpdated="22 mins ago", needsPickup=False),
]

@router.get("/bins", response_model=List[SmartBin])
async def get_bins():
    """Returns real-time IoT smart bins telemetry."""
    return DEMO_BINS

@router.get("/analytics")
async def get_analytics():
    """Returns historical performance benchmarking data for manual vs. AI collection."""
    return {
        "summary": {
            "totalItemsSorted": 14820,
            "overallAccuracyPercent": 96.4,
            "averageFuelSavedPercent": 50.2,
            "co2SavedTotalKg": 1420.5,
            "activeBinsCount": len(DEMO_BINS),
        },
        "historicalDays": [
            {"day": "Mon", "standardDistanceKm": 47.2, "aiDistanceKm": 23.8, "standardFuelLiters": 14.8, "aiFuelLiters": 7.2, "standardCo2Kg": 39.2, "aiCo2Kg": 19.1},
            {"day": "Tue", "standardDistanceKm": 48.5, "aiDistanceKm": 25.1, "standardFuelLiters": 15.1, "aiFuelLiters": 7.6, "standardCo2Kg": 40.1, "aiCo2Kg": 20.2},
            {"day": "Wed", "standardDistanceKm": 49.0, "aiDistanceKm": 22.4, "standardFuelLiters": 15.3, "aiFuelLiters": 6.9, "standardCo2Kg": 40.6, "aiCo2Kg": 18.3},
            {"day": "Thu", "standardDistanceKm": 46.8, "aiDistanceKm": 24.0, "standardFuelLiters": 14.6, "aiFuelLiters": 7.4, "standardCo2Kg": 38.7, "aiCo2Kg": 19.6},
            {"day": "Fri", "standardDistanceKm": 51.2, "aiDistanceKm": 26.5, "standardFuelLiters": 16.0, "aiFuelLiters": 8.1, "standardCo2Kg": 42.4, "aiCo2Kg": 21.5},
            {"day": "Sat", "standardDistanceKm": 44.5, "aiDistanceKm": 21.0, "standardFuelLiters": 13.9, "aiFuelLiters": 6.4, "standardCo2Kg": 36.8, "aiCo2Kg": 17.0},
            {"day": "Sun", "standardDistanceKm": 42.0, "aiDistanceKm": 19.5, "standardFuelLiters": 13.1, "aiFuelLiters": 5.9, "standardCo2Kg": 34.7, "aiCo2Kg": 15.6},
        ],
        "materialBreakdown": [
            {"material": "Plastic & Bottles", "itemsSorted": 5420, "accuracyPercent": 97.4, "binColor": "#2563EB"},
            {"material": "Food & Organic", "itemsSorted": 4890, "accuracyPercent": 96.8, "binColor": "#059669"},
            {"material": "Paper & Cardboard", "itemsSorted": 2640, "accuracyPercent": 95.2, "binColor": "#3B82F6"},
            {"material": "Hazardous & Batteries", "itemsSorted": 1180, "accuracyPercent": 98.9, "binColor": "#DC2626"},
            {"material": "Metal & Cans", "itemsSorted": 690, "accuracyPercent": 96.1, "binColor": "#64748B"},
        ]
    }
