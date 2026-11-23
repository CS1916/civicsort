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

def test_root_serves_html():
    print("Testing GET / serves standalone-preview.html...")
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "")
    assert "Computer Vision Waste Segregation" in res.text
    print(" GET / successfully serves standalone-preview.html")

def test_detect_image():
    print("Testing POST /detect-image with multi-object image...")
    # Create test image with multiple simulated colored objects
    img = np.full((480, 640, 3), 220, dtype=np.uint8)
    # Draw bottle-like shape (blue)
    cv2.rectangle(img, (80, 100), (160, 360), (220, 60, 40), -1)
    # Draw apple/fruit-like shape (green)
    cv2.circle(img, (320, 260), 60, (40, 200, 60), -1)
    # Draw battery/box shape (red)
    cv2.rectangle(img, (460, 180), (580, 320), (40, 40, 220), -1)

    _, buf = cv2.imencode(".jpg", img)
    files = {"file": ("test_litter.jpg", buf.tobytes(), "image/jpeg")}

    res = client.post("/detect-image", files=files)
    assert res.status_code == 200, f"detect-image failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "detections" in data
    assert len(data["detections"]) > 0
    assert "annotatedImage" in data
    assert "categoryCounts" in data
    print(f" Detected {len(data['detections'])} objects across categories: {data['categoryCounts']}")
    print(f" Sample detection: {data['detections'][0]['label']} ({data['detections'][0]['confidencePercent']}) -> {data['detections'][0]['category']}")

def test_detect_video():
    print("Testing POST /detect-video with test video...")
    # Generate 15-frame test video
    h, w = 360, 480
    video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads", "test_video_sample.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 15.0, (w, h))

    for i in range(15):
        frame = np.full((h, w, 3), 230, dtype=np.uint8)
        # Moving box across frames
        pos_x = 80 + i * 15
        cv2.rectangle(frame, (pos_x, 100), (pos_x + 80, 260), (200, 80, 50), -1)
        out.write(frame)
    out.release()

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    files = {"file": ("sample_clip.mp4", video_bytes, "video/mp4")}
    res = client.post("/detect-video", files=files)
    assert res.status_code == 200, f"detect-video failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "videoUrl" in data
    assert data["framesProcessed"] > 0
    assert "categoryCounts" in data
    print(f" Video processed successfully: {data['framesProcessed']} frames, URL: {data['videoUrl']}")
    print(f" Category counts: {data['categoryCounts']}")

    # Clean up test input video
    if os.path.exists(video_path):
        os.remove(video_path)

if __name__ == "__main__":
    print("Running Dense Multi-Object Detection & Video Processing Tests...")
    test_root_serves_html()
    test_detect_image()
    test_detect_video()
    print("\n All Backend Dense Detection & Video Tests Passed Successfully!")
