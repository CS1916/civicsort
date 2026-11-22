from fastapi import APIRouter, HTTPException
from app.models.schemas import OptimizeRouteRequest, OptimizeRouteResponse
from app.services.vrp_solver import optimize_waste_routes

router = APIRouter(prefix="/optimize-route", tags=["Intelligent Route Optimization"])

@router.post("", response_model=OptimizeRouteResponse)
async def optimize_route(request: OptimizeRouteRequest):
    """
    Computes mathematically optimal collection routes using Google OR-Tools and OSRM street network.
    Generates:
    1. Standard Route: baseline naive route visiting 100% of municipal bins.
    2. AI Smart Route: dynamically pruned and optimized path servicing ONLY bins with fillLevel >= threshold.
    Returns ordered GPS waypoints and precise metrics (distance saved, time saved, fuel saved, CO2 avoided).
    """
    if not request.bins:
        raise HTTPException(status_code=400, detail="At least one smart bin must be provided.")

    try:
        threshold = request.fillThreshold if request.fillThreshold is not None else 75.0
        response = optimize_waste_routes(
            bins=request.bins,
            depot=request.depot,
            fill_threshold=threshold,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route optimization solver failed: {e}")
