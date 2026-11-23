import os
import sys
import numpy as np
import cv2

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.yolo_service import detect_multi_objects_image, get_yolo_model

def test_person_vs_waste():
    print("Testing person vs. waste detection logic...")
    model = get_yolo_model()
    print("Loaded model classes count:", len(model.names))
    print("Class 0 is:", model.names.get(0)) # COCO class 0 is 'person'

    # Create a realistic test canvas with a simulated 'person' label and a 'bottle'
    # Test YOLO model names directly to ensure person filtering works
    from app.services.yolo_service import is_blocked_non_waste, map_raw_label
    assert is_blocked_non_waste(model.names.get(0)) is True, "COCO Class 0 (person) MUST be blocked!"
    assert map_raw_label(model.names.get(0)) is None, "COCO Class 0 (person) mapping MUST return None!"

    # Test bottle (COCO class 39)
    bottle_class = "bottle"
    assert is_blocked_non_waste(bottle_class) is False
    mapped = map_raw_label(bottle_class)
    assert mapped is not None
    assert mapped[2] == "Recyclable"
    print(f"Verified: {model.names.get(0)} is 100% blocked, and {bottle_class} is correctly categorized as {mapped[2]}!")

if __name__ == "__main__":
    test_person_vs_waste()
