from fastapi import APIRouter, HTTPException
from app.models.schemas import OptimizeRouteRequest, OptimizeRouteResponse
from app.services.vrp_solver import optimize_waste_routes

router = APIRouter(prefix="", tags=["Intelligent Route Optimization"])

@router.post("/routes/optimize", response_model=OptimizeRouteResponse)
@router.post("/optimize-route", response_model=OptimizeRouteResponse)
@router.post("/api/optimize-route", response_model=OptimizeRouteResponse)
async def optimize_route(request: OptimizeRouteRequest):
    """
    Computes optimal collection routes using Google OR-Tools and OSRM street network.
    Compares:
    1. Standard Route: naive sweep visiting all bins.
    2. AI Smart Route: mathematically optimized path servicing only full bins (>=75%).
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
