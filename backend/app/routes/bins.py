import io
import csv
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Response, HTTPException, Query
from pydantic import BaseModel
from app.database import (
    list_bins,
    get_bin,
    create_bin,
    update_bin,
    delete_bin,
    simulate_sensor_fluctuations,
    get_municipal_analytics,
)

router = APIRouter(prefix="", tags=["Smart Bins & Route Monitoring"])


class CreateBinPayload(BaseModel):
    name: str
    zone: str
    address: str
    lat: float
    lng: float
    category: str = "recyclable"
    fillLevel: float = 20.0
    capacityKg: float = 100.0
    priority: str = "Normal"


class UpdateBinPayload(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    fillLevel: Optional[float] = None
    priority: Optional[str] = None
    needsPickup: Optional[bool] = None


class BinUpdateDirect(BaseModel):
    binId: str
    fillLevel: float
    needsPickup: Optional[bool] = None


@router.get("/bins")
@router.get("/api/bins")
async def get_bins():
    """Returns smart bins and fill level data queried directly from database."""
    return list_bins()


@router.get("/bins/{bin_id}")
@router.get("/api/bins/{bin_id}")
async def get_single_bin(bin_id: str):
    b = get_bin(bin_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bin not found")
    return b


@router.post("/bins")
@router.post("/api/bins")
async def add_new_bin(payload: CreateBinPayload):
    """Adds a new municipal smart bin to the database."""
    new_bin = create_bin(payload.dict())
    return {"success": True, "bin": new_bin}


@router.put("/bins/{bin_id}")
@router.put("/api/bins/{bin_id}")
async def edit_bin(bin_id: str, payload: UpdateBinPayload):
    """Updates smart bin details, fill levels, or priority in database."""
    updated = update_bin(bin_id, {k: v for k, v in payload.dict().items() if v is not None})
    if not updated:
        raise HTTPException(status_code=404, detail="Bin not found")
    return {"success": True, "bin": updated}


@router.delete("/bins/{bin_id}")
@router.delete("/api/bins/{bin_id}")
async def remove_bin(bin_id: str):
    """Deletes a smart bin from the municipal grid (Admin permission)."""
    ok = delete_bin(bin_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bin not found")
    return {"success": True, "message": f"Bin {bin_id} deleted."}


@router.post("/bins/update")
@router.post("/api/bins/update")
async def update_bin_direct(payload: BinUpdateDirect):
    """Backward-compatible quick fill level update."""
    updated = update_bin(payload.binId, {"fillLevel": payload.fillLevel, "needsPickup": payload.needsPickup})
    if not updated:
        raise HTTPException(status_code=404, detail="Bin not found")
    return {"success": True, "bin": updated}


@router.post("/bins/simulate")
@router.post("/api/bins/simulate")
async def simulate_bins():
    """
    Simulates dynamic bin fill levels for collection route optimization testing.
    Clearly marked as simulated route-testing data.
    """
    updated_bins = simulate_sensor_fluctuations()
    critical_count = len([b for b in updated_bins if b["needsPickup"]])
    return {
        "success": True,
        "isSimulated": True,
        "source": "Simulated Route-Testing Fill Levels",
        "message": "Simulated fill levels updated across 12 city bins.",
        "bins": updated_bins,
        "criticalBinsCount": critical_count
    }


@router.get("/analytics")
@router.get("/api/analytics")
async def get_analytics():
    """Returns municipal historical benchmarking stats calculated from live database records."""
    return get_municipal_analytics()


@router.get("/reports/export")
@router.get("/api/reports/export")
async def export_report(format: str = Query("csv", pattern="^(csv|json)$")):
    """Generates and downloads a clean municipal audit report in CSV or JSON format."""
    bins = list_bins()
    analytics = get_municipal_analytics()

    if format == "json":
        report_data = {
            "title": "EcoRoute AI Municipal Smart Waste Audit Report",
            "jurisdiction": "Bengaluru Urban Municipal Operations",
            "authorizedOfficer": "Chethan (CS)",
            "generatedAt": "2026-11-23T01:00:00Z",
            "analyticsSummary": analytics["summary"],
            "bins": bins,
            "wasteTrends": analytics["wasteTrends7D"],
            "zonePurity": analytics["zoneFillRates"],
        }
        return Response(
            content=json.dumps(report_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=EcoRoute_AI_Audit_Report.json"}
        )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["=== ECOROUTE AI MUNICIPAL SMART WASTE AUDIT REPORT ==="])
    writer.writerow(["Jurisdiction", "Bengaluru Urban Municipal Operations"])
    writer.writerow(["Authorized Officer", "Chethan (CS)"])
    writer.writerow([])

    writer.writerow(["METRIC SUMMARY", "VALUE"])
    writer.writerow(["Segregation Purity Rate", f"{analytics['summary']['segregationRatePercent']}% (YOLOv8s Verified)"])
    writer.writerow(["Active Bins Monitored", f"{len(bins)} Smart Bins"])
    writer.writerow(["Total Fuel Saved", f"{analytics['summary']['fuelSavedLiters']} Liters"])
    writer.writerow(["CO2 Abatement", f"{analytics['summary']['co2SavedTotalKg']} kg CO2"])
    writer.writerow(["Trees Saved Equivalent", f"{analytics['summary']['treesEquivalent']} Trees"])
    writer.writerow([])

    writer.writerow(["LIVE BENGALURU SMART BIN STATUS"])
    writer.writerow(["Bin Code", "Name", "Zone", "Address", "Fill Level (%)", "Category", "Priority", "Battery (%)", "Pickup Required"])
    for b in bins:
        writer.writerow([
            b["code"],
            b["name"],
            b["zone"],
            b["address"],
            f"{b['fillLevel']}%",
            b["category"],
            b.get("priority", "Normal"),
            f"{b['batteryLevel']}%",
            "YES" if b["needsPickup"] else "NO"
        ])

    writer.writerow([])
    writer.writerow(["7-DAY FLEET OPTIMIZATION LOG"])
    writer.writerow(["Day", "Standard Route (km)", "AI Smart Route (km)", "Distance Saved (km)", "Diesel Saved (L)", "CO2 Avoided (kg)"])
    for t in analytics["wasteTrends7D"]:
        dist_saved = round(t["standardKm"] - t["aiKm"], 1)
        writer.writerow([t["day"], t["standardKm"], t["aiKm"], f"{dist_saved} km", t["fuelSavedL"], t["co2SavedKg"]])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=EcoRoute_AI_Audit_Report.csv"}
    )
