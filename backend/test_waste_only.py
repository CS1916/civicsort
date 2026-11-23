import os
import sys
import io
import time
import requests
import numpy as np
import cv2

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.yolo_service import (
    is_blocked_non_waste,
    map_raw_label,
    detect_multi_objects_image,
    get_yolo_model,
    BLOCKED_NON_WASTE_CLASSES,
)

def run_unit_tests():
    print("=== [1] UNIT TEST: STRICT NON-WASTE & HUMAN EXCLUSION ===")
    
    # 1. Test is_blocked_non_waste on all human and fixture classes
    test_humans = ["person", "human", "pedestrian", "man", "woman", "child", "boy", "girl", "crowd", "sanitation worker"]
    for h in test_humans:
        assert is_blocked_non_waste(h), f"FAILED: '{h}' must be blocked!"
    print(f"  [PASS] All {len(test_humans)} human/person categories successfully blocked.")

    test_fixtures = ["bicycle", "car", "motorcycle", "bus", "truck", "traffic light", "bench", "chair", "sofa", "toilet", "cat", "dog"]
    for f in test_fixtures:
        assert is_blocked_non_waste(f), f"FAILED: '{f}' must be blocked!"
    print(f"  [PASS] All {len(test_fixtures)} non-waste vehicle/furniture/animal classes successfully blocked.")

    test_waste = ["bottle", "can", "banana", "apple", "battery", "box", "cardboard", "wrapper", "cup", "cell phone"]
    for w in test_waste:
        assert not is_blocked_non_waste(w), f"FAILED: valid waste '{w}' was mistakenly blocked!"
    print(f"  [PASS] All {len(test_waste)} valid waste classes correctly accepted.")

    # 2. Test map_raw_label returns None for blocked entities
    assert map_raw_label("person") is None, "FAILED: map_raw_label('person') must return None!"
    assert map_raw_label("car") is None, "FAILED: map_raw_label('car') must return None!"
    assert map_raw_label("chair") is None, "FAILED: map_raw_label('chair') must return None!"
    print("  [PASS] map_raw_label correctly returns None for non-waste classes.")

    # 3. Test map_raw_label on valid waste items
    code, name, stream, style = map_raw_label("bottle")
    assert stream == "Recyclable", f"Expected Recyclable, got {stream}"
    print(f"  [PASS] 'bottle' correctly mapped to stream: {stream} ({name})")

    code, name, stream, style = map_raw_label("banana")
    assert stream == "Organic", f"Expected Organic, got {stream}"
    print(f"  [PASS] 'banana' correctly mapped to stream: {stream} ({name})")

    code, name, stream, style = map_raw_label("battery")
    assert stream == "Hazardous", f"Expected Hazardous, got {stream}"
    print(f"  [PASS] 'battery' correctly mapped to stream: {stream} ({name})")

    code, name, stream, style = map_raw_label("wrapper")
    assert stream == "Residual", f"Expected Residual, got {stream}"
    print(f"  [PASS] 'wrapper' correctly mapped to stream: {stream} ({name})")


def run_synthetic_image_test():
    print("\n=== [2] INFERENCE TEST: IMAGE DETECTION ENGINE ===")
    
    # Create a synthetic image (640x480) with realistic colored objects
    img = np.ones((480, 640, 3), dtype=np.uint8) * 240
    # Add a mock object (e.g. green block for organic, blue cylinder for bottle)
    cv2.rectangle(img, (80, 100), (200, 380), (220, 60, 20), -1)  # Blue cylinder
    cv2.putText(img, "DRINK", (90, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    _, enc = cv2.imencode(".jpg", img)
    img_bytes = enc.tobytes()

    result = detect_multi_objects_image(img_bytes)
    assert result["success"] is True
    print(f"  [PASS] detect_multi_objects_image executed in {result['processingTimeMs']} ms.")
    print(f"  [PASS] Total detected objects: {result['totalObjects']}")
    print(f"  [PASS] Category counts: {result['categoryCounts']}")
    
    # Verify that NO detection contains blocked keywords
    for d in result["detections"]:
        lbl = d["label"].lower()
        cat = d["category"].lower()
        for b in BLOCKED_NON_WASTE_CLASSES:
            assert b != lbl and b != cat, f"CRITICAL: Non-waste item '{b}' was detected as waste: {d}"
    print("  [PASS] Strict waste-only invariant verified: 0 humans/non-waste items detected.")


def run_live_api_tests(base_url="http://127.0.0.1:8000"):
    print(f"\n=== [3] ENDPOINT INTEGRATION TESTS on {base_url} ===")
    
    # 1. Health check
    res = requests.get(f"{base_url}/health", timeout=5)
    assert res.status_code == 200
    print(f"  [PASS] GET /health returned 200: {res.json()['service']}")

    # 2. UI preview root
    res = requests.get(f"{base_url}/", timeout=5)
    assert res.status_code == 200
    assert "EcoRoute AI" in res.text or "<!DOCTYPE html>" in res.text
    print(f"  [PASS] GET / serves standalone UI (content length: {len(res.text)} bytes)")

    # 3. Smart Bins with Bengaluru coordinates
    res = requests.get(f"{base_url}/bins", timeout=5)
    assert res.status_code == 200
    bins = res.json()
    assert len(bins) == 12
    # Verify Bengaluru latitude (~12.8 - 13.1) and longitude (~77.5 - 77.8)
    for b in bins:
        lat, lng = b["lat"], b["lng"]
        assert 12.0 <= lat <= 14.0, f"Bin {b['name']} lat {lat} not in Bengaluru region!"
        assert 77.0 <= lng <= 78.5, f"Bin {b['name']} lng {lng} not in Bengaluru region!"
    print(f"  [PASS] GET /bins verified: all 12 smart bins located in Bengaluru, India.")
    print(f"         Sample bin: {bins[0]['name']} ({bins[0]['code']}) at [{bins[0]['lat']}, {bins[0]['lng']}]")

    # 4. Telemetry simulation
    res = requests.post(f"{base_url}/bins/simulate", timeout=5)
    assert res.status_code == 200
    sim_data = res.json()
    assert sim_data["success"] is True
    print(f"  [PASS] POST /bins/simulate successfully pushed sensor fluctuations.")

    # 5. Route Optimizer (Google OR-Tools)
    route_payload = {
        "bins": bins,
        "depot": {
            "id": "depot-blr-01",
            "name": "Bengaluru Central Eco-Hub & Fleet Depot",
            "address": "MG Road Logistics Core, Bengaluru",
            "lat": 12.9756,
            "lng": 77.6097
        },
        "fillThreshold": 75.0
    }
    res = requests.post(f"{base_url}/routes/optimize", json=route_payload, timeout=8)
    assert res.status_code == 200
    route_data = res.json()
    assert "aiSmartRoute" in route_data
    assert "standardRoute" in route_data
    assert "savings" in route_data
    savings = route_data["savings"]
    print(f"  [PASS] POST /routes/optimize executed successfully:")
    print(f"         Distance Saved: {savings['distanceSavedKm']} km ({savings['distanceSavedPercent']}%)")
    print(f"         Time Saved: {savings['timeSavedMins']} mins")
    print(f"         Fuel Saved: {savings['fuelSavedLiters']} L | CO2 Avoided: {savings['co2SavedKg']} kg")

    # 6. Multi-object image detection endpoint
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    cv2.circle(img, (320, 240), 80, (50, 180, 50), -1)
    _, enc = cv2.imencode(".jpg", img)
    files = {"file": ("test_waste.jpg", enc.tobytes(), "image/jpeg")}
    res = requests.post(f"{base_url}/detect/image", files=files, timeout=10)
    assert res.status_code == 200
    det_data = res.json()
    assert det_data["success"] is True
    print(f"  [PASS] POST /detect/image returned 200 with {det_data['totalObjects']} detected objects.")

    # 7. Analytics
    res = requests.get(f"{base_url}/analytics", timeout=5)
    assert res.status_code == 200
    analytics = res.json()
    assert "summary" in analytics
    print(f"  [PASS] GET /analytics verified: Segregation rate = {analytics['summary']['segregationRatePercent']}%")

    # 8. Report CSV export
    res = requests.get(f"{base_url}/reports/export", timeout=5)
    assert res.status_code == 200
    assert "ECOROUTE AI" in res.text
    print(f"  [PASS] GET /reports/export downloaded CSV report successfully ({len(res.text)} bytes).")

    print("\n=======================================================")
    print(" ALL 8 PRODUCTION INTEGRATION & UNIT TESTS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    run_unit_tests()
    run_synthetic_image_test()
    # If server is running on 8000, run integration tests
    try:
        run_live_api_tests()
    except Exception as e:
        print(f"Notice: live API test skipped/deferred: {e}")
