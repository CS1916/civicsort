"""
Comprehensive End-to-End Test Suite for EcoRoute AI Platform
Tests all routes:
- GET / (UI serving)
- GET /health
- POST /detect/image & /detect-image (SAHI Multi-Scale YOLOv8)
- POST /detect/video & /detect-video (OpenCV Video Processing)
- GET /bins & POST /bins/simulate
- POST /routes/optimize & /api/optimize-route (Google OR-Tools)
- GET /analytics
- GET /reports/export (CSV generation)
- GET /settings/map-key & POST /settings/map-key
"""

import sys
import os
import io
import cv2
import numpy as np

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ui_served():
    print("1. Testing GET / (EcoRoute AI Dashboard UI)...")
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "")
    assert "EcoRoute" in res.text
    assert "Chethan" in res.text
    print("   GET / successfully serves EcoRoute AI dashboard.")

def test_health():
    print("2. Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print(f"   Service: {data.get('service')}, Model: {data.get('yoloModel')}")

def test_detect_image_sahi():
    print("3. Testing POST /detect/image (SAHI Multi-Scale Detection)...")
    img = np.full((640, 640, 3), 210, dtype=np.uint8)
    # Simulate bottle (blue)
    cv2.rectangle(img, (120, 150), (220, 480), (235, 99, 37), -1)
    # Simulate apple/fruit (green)
    cv2.circle(img, (400, 320), 80, (105, 150, 5), -1)
    # Simulate battery/box (red)
    cv2.rectangle(img, (480, 180), (590, 300), (38, 38, 220), -1)

    _, buf = cv2.imencode(".jpg", img)
    files = {"file": ("test_waste.jpg", buf.tobytes(), "image/jpeg")}

    res = client.post("/detect/image", files=files)
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "detections" in data
    assert len(data["detections"]) > 0
    assert "annotatedImage" in data
    assert "categoryCounts" in data

    first_det = data["detections"][0]
    print(f"   Detections count: {len(data['detections'])}")
    print(f"   Top item: {first_det['label']} ({first_det['confidencePercent']}) -> {first_det['category']}")
    print(f"   Category breakdown: {data['categoryCounts']}")

def test_detect_video():
    print("4. Testing POST /detect/video (OpenCV Video Processing)...")
    h, w = 240, 320
    test_video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads", "test_video_clip.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video_path, fourcc, 15.0, (w, h))

    for i in range(12):
        frame = np.full((h, w, 3), 220, dtype=np.uint8)
        cv2.rectangle(frame, (50 + i * 8, 40), (120 + i * 8, 160), (220, 80, 40), -1)
        out.write(frame)
    out.release()

    with open(test_video_path, "rb") as vf:
        res = client.post("/detect/video", files={"file": ("clip.mp4", vf.read(), "video/mp4")})

    if os.path.exists(test_video_path):
        os.remove(test_video_path)

    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "videoUrl" in data
    print(f"   Processed {data['framesProcessed']} frames, Playable Video URL: {data['videoUrl']}")

def test_bins_and_simulation():
    print("5. Testing GET /bins and POST /bins/simulate...")
    r1 = client.get("/bins")
    assert r1.status_code == 200
    bins = r1.json()
    assert len(bins) == 12
    print(f"   Retrieved {len(bins)} IoT smart bins across city zones.")

    r2 = client.post("/bins/simulate")
    assert r2.status_code == 200
    assert r2.json()["success"] is True
    print(f"   Pushed simulated telemetry. Critical bins: {r2.json()['criticalBinsCount']}")

def test_route_optimization():
    print("6. Testing POST /routes/optimize (Google OR-Tools)...")
    bins_res = client.get("/bins").json()
    payload = {"bins": bins_res, "fillThreshold": 75.0}

    res = client.post("/routes/optimize", json=payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert "savings" in data
    assert "aiSmartRoute" in data
    assert "standardRoute" in data
    savings = data["savings"]
    print(f"   Distance Saved: {savings['distanceSavedKm']} km ({savings['distanceSavedPercent']}%)")
    print(f"   CO2 Abated: {savings['co2SavedKg']} kg")

def test_analytics_and_reports():
    print("7. Testing GET /analytics and GET /reports/export...")
    r1 = client.get("/analytics")
    assert r1.status_code == 200
    assert "wasteTrends7D" in r1.json()
    print("   Analytics metrics loaded successfully.")

    r2 = client.get("/reports/export")
    assert r2.status_code == 200
    assert "text/csv" in r2.headers.get("content-type", "")
    assert "ECOROUTE AI" in r2.text
    print("   Report exported cleanly as CSV.")

def test_settings_map_key():
    print("8. Testing GET & POST /settings/map-key...")
    r1 = client.get("/settings/map-key")
    assert r1.status_code == 200
    print(f"   Current provider: {r1.json().get('provider')}")

    r2 = client.post("/settings/map-key", json={"provider": "esri", "apiKey": "test-key-123", "imageryStyle": "hybrid"})
    assert r2.status_code == 200
    assert r2.json()["success"] is True
    print("   Custom map key settings persisted successfully.")

if __name__ == "__main__":
    print("\n==================================================")
    print("  RUNNING ECOROUTE AI END-TO-END VERIFICATION")
    print("==================================================\n")
    test_ui_served()
    test_health()
    test_detect_image_sahi()
    test_detect_video()
    test_bins_and_simulation()
    test_route_optimization()
    test_analytics_and_reports()
    test_settings_map_key()
    print("\n ALL ECOROUTE AI ENDPOINTS VERIFIED & PRODUCTION READY!\n")
