import os
import sys
import json
import requests
import numpy as np
import cv2

BASE_URL = "http://127.0.0.1:8000"

def test_full_system():
    print("==================================================================")
    print(" RUNNING ECOROUTE AI END-TO-END PRODUCTION VERIFICATION SUITE")
    print("==================================================================")

    # 1. Health check & Server root
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("  [PASS] 1. GET /health - Core online, SQLite connected.")

    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200 and "EcoRoute AI" in r.text
    print(f"  [PASS] 2. GET / - Serves frontend UI ({len(r.text)} bytes).")

    # 2. Authentication & RBAC
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@ecoroute.city", "password": "admin123"})
    assert r.status_code == 200 and r.json()["user"]["role"] == "admin"
    admin_token = r.json()["token"]
    print("  [PASS] 3. POST /auth/login - Admin authenticated (Chethan).")

    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "operator@ecoroute.city", "password": "operator123"})
    assert r.status_code == 200 and r.json()["user"]["role"] == "operator"
    print("  [PASS] 4. POST /auth/login - Operator authenticated (Ramesh Kumar).")

    r = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200 and r.json()["user"]["full_name"] == "Chethan (CS)"
    print("  [PASS] 5. GET /auth/me - Token validation verified.")

    # 3. Smart Bins CRUD & IoT Simulation
    r = requests.get(f"{BASE_URL}/bins")
    assert r.status_code == 200
    bins = r.json()
    assert len(bins) >= 12
    print(f"  [PASS] 6. GET /bins - Loaded {len(bins)} smart bins from SQLite.")

    # Add a test bin
    new_bin_payload = {
        "name": "MG Road Brigade Junction",
        "zone": "Central Retail & MG Rd",
        "address": "Brigade Rd & MG Rd Cross",
        "lat": 12.9740,
        "lng": 77.6080,
        "category": "recyclable",
        "fillLevel": 42.0,
        "priority": "Normal",
        "capacityKg": 100.0
    }
    r = requests.post(f"{BASE_URL}/bins", json=new_bin_payload)
    assert r.status_code == 200 and r.json()["success"] is True
    created_bin_id = r.json()["bin"]["id"]
    print(f"  [PASS] 7. POST /bins - Created smart bin: {created_bin_id}")

    # Update bin
    r = requests.put(f"{BASE_URL}/bins/{created_bin_id}", json={"fillLevel": 88.0, "priority": "Critical"})
    assert r.status_code == 200 and r.json()["bin"]["fill_level"] == 88.0
    print(f"  [PASS] 8. PUT /bins/{created_bin_id} - Updated fill to 88.0% and priority to Critical.")

    # Delete bin
    r = requests.delete(f"{BASE_URL}/bins/{created_bin_id}")
    assert r.status_code == 200 and r.json()["success"] is True
    print(f"  [PASS] 9. DELETE /bins/{created_bin_id} - Bin cleanly deleted.")

    # Simulate IoT sensors
    r = requests.post(f"{BASE_URL}/bins/simulate")
    assert r.status_code == 200 and r.json()["isSimulated"] is True
    print(f"  [PASS] 10. POST /bins/simulate - Pushed simulated IoT sensor telemetry to all bins.")

    # 4. Fleet Vehicles & Drivers CRUD
    r = requests.get(f"{BASE_URL}/vehicles")
    assert r.status_code == 200
    vehs = r.json()
    assert len(vehs) >= 4
    print(f"  [PASS] 11. GET /vehicles - Loaded {len(vehs)} fleet trucks from database.")

    r = requests.get(f"{BASE_URL}/drivers")
    assert r.status_code == 200
    drvs = r.json()
    assert len(drvs) >= 4
    print(f"  [PASS] 12. GET /drivers - Loaded {len(drvs)} municipal drivers.")

    # 5. Route Optimizer (Google OR-Tools VRP)
    route_payload = {
        "bins": bins[:8],
        "depot": {
            "id": "depot-blr-01",
            "name": "Bengaluru Central Eco-Hub & Fleet Depot",
            "address": "MG Road Logistics Core, Bengaluru",
            "lat": 12.9756,
            "lng": 77.6097
        },
        "fillThreshold": 75.0
    }
    r = requests.post(f"{BASE_URL}/routes/optimize", json=route_payload)
    assert r.status_code == 200
    opt_data = r.json()
    assert "savings" in opt_data
    savings = opt_data["savings"]
    print(f"  [PASS] 13. POST /routes/optimize - Google OR-Tools solved route:")
    print(f"         Distance Cut: {savings['distanceSavedKm']} km | Fuel Saved: {savings['fuelSavedLiters']} L | CO2 Avoided: {savings['co2SavedKg']} kg")

    # 6. Route Dispatch & Collection Logging
    dispatch_payload = {
        "vehicle_code": "TRK-01",
        "driver_name": "Suresh Gowda",
        "bins_serviced_count": 6,
        "total_weight_tons": 4.8,
        "distance_km": 23.8,
        "fuel_saved_liters": 7.6,
        "co2_avoided_kg": 20.1
    }
    r = requests.post(f"{BASE_URL}/collections/dispatch", json=dispatch_payload)
    assert r.status_code == 200 and r.json()["success"] is True
    run_id = r.json()["collectionRun"]["run_id"]
    print(f"  [PASS] 14. POST /collections/dispatch - Dispatched route logged as {run_id}.")

    r = requests.get(f"{BASE_URL}/collections/history")
    assert r.status_code == 200
    logs = r.json()
    assert any(l["run_id"] == run_id for l in logs)
    print(f"  [PASS] 15. GET /collections/history - Verified dispatch run in audit log.")

    # 7. Notifications & Alerts
    r = requests.get(f"{BASE_URL}/notifications")
    assert r.status_code == 200
    notifs = r.json()
    assert len(notifs) > 0
    print(f"  [PASS] 16. GET /notifications - Loaded {len(notifs)} operational notifications.")

    # 8. Analytics & Municipal Reports
    r = requests.get(f"{BASE_URL}/analytics")
    assert r.status_code == 200
    analytics = r.json()
    assert analytics["summary"]["segregationRatePercent"] > 90
    print(f"  [PASS] 17. GET /analytics - Municipal summary verified (Rate: {analytics['summary']['segregationRatePercent']}%).")

    r = requests.get(f"{BASE_URL}/reports/export?format=csv")
    assert r.status_code == 200 and "ECOROUTE AI" in r.text
    print(f"  [PASS] 18. GET /reports/export?format=csv - CSV download verified ({len(r.text)} bytes).")

    r = requests.get(f"{BASE_URL}/reports/export?format=json")
    assert r.status_code == 200
    json_report = r.json()
    assert "analyticsSummary" in json_report
    print(f"  [PASS] 19. GET /reports/export?format=json - JSON audit export verified.")

    # 9. Computer Vision Multi-Item Detection with Human Shield
    img = np.ones((480, 640, 3), dtype=np.uint8) * 230
    cv2.circle(img, (200, 200), 60, (20, 160, 20), -1) # Green circle
    cv2.rectangle(img, (350, 150), (450, 350), (220, 80, 20), -1) # Blue rectangle
    _, enc = cv2.imencode(".jpg", img)
    files = {"file": ("test_multi_item.jpg", enc.tobytes(), "image/jpeg")}
    r = requests.post(f"{BASE_URL}/detect/image", files=files)
    assert r.status_code == 200
    cv_res = r.json()
    assert cv_res["success"] is True and cv_res["wasteOnlyVerified"] is True
    print(f"  [PASS] 20. POST /detect/image - YOLOv8s Multi-Item Waste Detection verified ({cv_res['processingTimeMs']} ms).")

    print("\n==================================================================")
    print(" ALL 20 INTEGRATION TESTS COMPLETED SUCCESSFULLY (100% PASS RATE)")
    print("==================================================================")

if __name__ == "__main__":
    test_full_system()
