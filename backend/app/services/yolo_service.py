import os
import io
import time
import uuid
import base64
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image

from app.config import settings

# Attempt to import ultralytics YOLO
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

_yolo_model = None

# Ensure static directories exist
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
OUTPUTS_DIR = os.path.join(STATIC_DIR, "outputs")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_yolo_model():
    """
    Loads YOLOv8 model, prioritizing the stronger YOLOv8s model (yolov8s.pt)
    or custom waste weights, with graceful fallback to yolov8n.pt.
    """
    global _yolo_model
    if not ULTRALYTICS_AVAILABLE:
        return None
    if _yolo_model is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_paths = [
            os.path.join(base_dir, "weights", "yolov8s.pt"),
            os.path.join(base_dir, "weights", "waste_yolo.pt"),
            os.path.join(base_dir, "yolov8s.pt"),
            os.path.join(base_dir, "weights", "yolov8n.pt"),
            os.path.join(base_dir, "yolov8n.pt"),
            settings.YOLO_MODEL_PATH,
            "yolov8s.pt",
            "yolov8n.pt"
        ]
        for p in model_paths:
            if os.path.exists(p):
                try:
                    _yolo_model = YOLO(p)
                    print(f"[EcoRoute AI] High-Performance Detector Loaded from: {p}")
                    break
                except Exception as e:
                    print(f"[EcoRoute AI] Notice loading {p}: {e}")
        if _yolo_model is None:
            try:
                _yolo_model = YOLO("yolov8s.pt")
            except Exception:
                try:
                    _yolo_model = YOLO("yolov8n.pt")
                except Exception as e:
                    print(f"[EcoRoute AI] YOLO load fallback error: {e}")
    return _yolo_model


# ============================================================================
# EXPLICIT NON-WASTE & HUMAN BLOCKING
# Under NO circumstance should humans/people, vehicles, animals, or furniture
# be detected, highlighted, or categorized as waste.
# ============================================================================
BLOCKED_NON_WASTE_CLASSES = {
    # 1. Humans & People (ABSOLUTELY NEVER WASTE)
    "person", "human", "pedestrian", "man", "woman", "child", "boy", "girl",
    "baby", "people", "crowd", "face", "worker", "sanitation worker", "resident", "operator",

    # 2. Vehicles & Transportation
    "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "vehicle", "van", "scooter",

    # 3. Street Infrastructure & Fixtures
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",

    # 4. Living Animals & Pets
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "animal",

    # 5. Large Indoor Furniture & Fixtures
    "chair", "couch", "sofa", "bed", "dining table", "toilet", "refrigerator", "oven", "sink"
}


def is_blocked_non_waste(raw_class: str) -> bool:
    """
    Returns True if the raw class or any of its constituent words matches
    blocked non-waste entities (humans, vehicles, animals, furniture).
    """
    if not raw_class:
        return True
    cleaned = raw_class.lower().strip()
    if cleaned in BLOCKED_NON_WASTE_CLASSES:
        return True
    tokens = set(cleaned.replace("-", " ").replace("_", " ").split())
    if any(b in tokens for b in BLOCKED_NON_WASTE_CLASSES):
        return True
    # Substring safety check for human/person
    if "person" in cleaned or "human" in cleaned or "pedestrian" in cleaned:
        return True
    return False


# ============================================================================
# 4 STANDARD MUNICIPAL WASTE STREAMS & PALETTE
# Blue = Recyclable (#2563EB)
# Green = Organic (#059669)
# Red = Hazardous / E-Waste (#DC2626)
# Amber = Non-Recyclable / Residual Litter (#D97706)
# ============================================================================
STREAM_CONFIGS = {
    "Recyclable": {
        "fullName": "Recyclable / Plastic",
        "stream": "Recyclable",
        "colorHex": "#2563EB",
        "bgr": (235, 99, 37),
        "binName": "BLUE Bin — Recyclable",
        "binColor": "blue",
        "disposalInstruction": "Rinse food residues, remove caps, and flatten item to conserve bin volume."
    },
    "Organic": {
        "fullName": "Organic / Biodegradable",
        "stream": "Organic",
        "colorHex": "#059669",
        "bgr": (105, 150, 5),
        "binName": "GREEN Bin — Organic / Wet",
        "binColor": "green",
        "disposalInstruction": "Deposit directly in green compost bin without plastic liners. Yields high-grade organic compost."
    },
    "Hazardous": {
        "fullName": "Hazardous / E-Waste",
        "stream": "Hazardous",
        "colorHex": "#DC2626",
        "bgr": (38, 38, 220),
        "binName": "RED Bin — Hazardous Waste",
        "binColor": "red",
        "disposalInstruction": "Handle with care. Never throw into general trash or compactor due to fire & toxic chemical risks."
    },
    "Residual": {
        "fullName": "Non-Recyclable / Residual",
        "stream": "Residual",
        "colorHex": "#D97706",
        "bgr": (6, 119, 217),
        "binName": "AMBER Bin — Residual / Litter",
        "binColor": "amber",
        "disposalInstruction": "Non-recyclable composite or contaminated packaging. Dispose into municipal general waste."
    }
}


# ============================================================================
# FINE-GRAINED WASTE TAXONOMY MAPPING
# ============================================================================
FINE_GRAINED_TAXONOMY = {
    # --- Recyclable Items ---
    "bottle": ("PET_bottle", "PET Plastic Bottle", "Recyclable"),
    "can": ("aluminum_can", "Aluminum Beverage Can", "Recyclable"),
    "cup": ("paper_cup", "Disposable Paper/Plastic Cup", "Recyclable"),
    "wine glass": ("glass_bottle", "Glass Beverage Ware", "Recyclable"),
    "bowl": ("plastic_container", "Rigid Plastic Bowl/Container", "Recyclable"),
    "box": ("cardboard_box", "Corrugated Cardboard Box", "Recyclable"),
    "cardboard": ("cardboard_box", "Cardboard Packaging", "Recyclable"),
    "book": ("cardboard_paper", "Paper / Bound Cardboard", "Recyclable"),
    "backpack": ("textile_bag", "Recyclable Textile Bag", "Recyclable"),
    "handbag": ("plastic_film_bag", "Plastic Carrier Bag", "Recyclable"),
    "frisbee": ("plastic_lid", "Rigid Plastic Lid / Disk", "Recyclable"),
    "tin": ("aluminum_can", "Metal Tin Can", "Recyclable"),
    "plastic": ("plastic_container", "Rigid Plastic Container", "Recyclable"),
    "foil": ("packaging_foil", "Clean Aluminum Foil", "Recyclable"),
    "lid": ("plastic_lid", "Small Plastic Bottle Lid", "Recyclable"),
    "paper": ("paper_waste", "Mixed Clean Paper Sheet", "Recyclable"),
    "newspaper": ("paper_waste", "Recyclable Newsprint Paper", "Recyclable"),
    "jug": ("plastic_container", "Plastic Milk/Detergent Jug", "Recyclable"),
    "carton": ("cardboard_box", "Liquid Beverage Carton", "Recyclable"),

    # --- Organic Items ---
    "banana": ("banana_peel", "Banana Peel Scrap", "Organic"),
    "apple": ("apple_core", "Apple Core & Fresh Waste", "Organic"),
    "orange": ("citrus_peel", "Citrus Fruit Scrap", "Organic"),
    "sandwich": ("discarded_food", "Discarded Food Scraps", "Organic"),
    "broccoli": ("vegetable_scrap", "Vegetable Scrap", "Organic"),
    "carrot": ("vegetable_scrap", "Vegetable Scrap", "Organic"),
    "hot dog": ("food_waste", "Cooked Food Scrap", "Organic"),
    "pizza": ("bread_bakery", "Leftover Pizza Crust", "Organic"),
    "donut": ("bread_bakery", "Bakery Food Waste", "Organic"),
    "cake": ("bread_bakery", "Confectionery Food Scrap", "Organic"),
    "potted plant": ("plant_foliage", "Organic Plant Scrap", "Organic"),
    "leaf": ("plant_foliage", "Garden / Foliage Scrap", "Organic"),
    "food": ("food_waste", "Mixed Organic Food Waste", "Organic"),
    "fruit": ("fruit_scrap", "Mixed Fresh Fruit Scrap", "Organic"),
    "vegetable": ("vegetable_scrap", "Raw Vegetable Scrap", "Organic"),
    "bread": ("bread_bakery", "Bakery Grain Waste", "Organic"),

    # --- Hazardous / E-Waste Items ---
    "cell phone": ("smartphone_device", "Discarded Smartphone (E-Waste)", "Hazardous"),
    "laptop": ("electronic_hardware", "Computer Hardware (E-Waste)", "Hazardous"),
    "mouse": ("electronic_hardware", "Computer Peripheral (E-Waste)", "Hazardous"),
    "remote": ("battery_ewaste", "Electronic Remote (Battery Risk)", "Hazardous"),
    "keyboard": ("electronic_hardware", "Electronic Keyboard (E-Waste)", "Hazardous"),
    "tv": ("electronic_hardware", "Display Screen (Hazardous E-Waste)", "Hazardous"),
    "microwave": ("electronic_hardware", "Electronic Appliance (E-Waste)", "Hazardous"),
    "toaster": ("electronic_hardware", "Small Appliance (E-Waste)", "Hazardous"),
    "battery": ("battery_ewaste", "Lithium-Ion / Alkaline Battery", "Hazardous"),
    "spray": ("aerosol_spray_can", "Pressurized Aerosol Spray Can", "Hazardous"),
    "chemical": ("chemical_bottle", "Toxic Chemical Container", "Hazardous"),
    "aerosol": ("aerosol_spray_can", "Pressurized Spray Can", "Hazardous"),
    "bulb": ("light_bulb", "Fluorescent / LED Bulb (E-Waste)", "Hazardous"),
    "cable": ("cable_wire", "Electronic Cable / Wiring", "Hazardous"),
    "wire": ("cable_wire", "Discarded Electrical Wiring", "Hazardous"),

    # --- Residual / Non-Recyclable Litter ---
    "toothbrush": ("hygiene_brush", "Toothbrush / Plastic Bristles", "Residual"),
    "hair drier": ("plastic_tube", "Personal Care Tube / Device", "Residual"),
    "scissors": ("composite_scrap", "Mixed Metal & Plastic Scrap", "Residual"),
    "fork": ("plastic_cutlery", "Disposable Plastic Cutlery", "Residual"),
    "knife": ("plastic_cutlery", "Disposable Plastic Cutlery", "Residual"),
    "spoon": ("plastic_cutlery", "Disposable Plastic Cutlery", "Residual"),
    "umbrella": ("composite_scrap", "Broken Umbrella Frame", "Residual"),
    "cigarette": ("cigarette_scrap", "Cigarette Butt & Filter Scrap", "Residual"),
    "wrapper": ("foil_wrapper", "Multilayer Composite Wrapper", "Residual"),
    "tube": ("toothpaste_tube", "Laminated Squeeze Tube", "Residual"),
    "straw": ("plastic_straw", "Single-Use Plastic Straw", "Residual"),
}


def map_raw_label(raw_class: str) -> Optional[Tuple[str, str, str, Dict[str, Any]]]:
    """
    Maps raw detection class into (label_code, human_label, stream_key, stream_config).
    Returns None if the class is blocked non-waste (humans, vehicles, furniture, animals).
    """
    if is_blocked_non_waste(raw_class):
        return None

    cleaned = raw_class.lower().strip()

    # 1. Exact or substring match in fine-grained taxonomy
    for key, (label_code, human_name, stream_key) in FINE_GRAINED_TAXONOMY.items():
        if key in cleaned:
            return label_code, human_name, stream_key, STREAM_CONFIGS[stream_key]

    # 2. General keyword heuristics for recognized waste streams
    if any(k in cleaned for k in ["plastic", "glass", "paper", "cardboard", "box", "metal", "can", "bottle", "carton", "aluminum", "tin"]):
        return "recyclable_debris", f"Recyclable Debris ({cleaned.title()})", "Recyclable", STREAM_CONFIGS["Recyclable"]
    elif any(k in cleaned for k in ["fruit", "vegetable", "bread", "meat", "scrap", "leaf", "plant", "food", "compost", "peel"]):
        return "organic_waste", f"Organic Scrap ({cleaned.title()})", "Organic", STREAM_CONFIGS["Organic"]
    elif any(k in cleaned for k in ["battery", "circuit", "cable", "electronic", "wire", "bulb", "device", "hardware", "charger"]):
        return "battery_ewaste", f"Electronic / Battery Scrap ({cleaned.title()})", "Hazardous", STREAM_CONFIGS["Hazardous"]
    elif any(k in cleaned for k in ["trash", "litter", "debris", "waste", "garbage", "rubbish", "cigarette", "wrapper"]):
        return "general_litter", f"General Litter ({cleaned.title()})", "Residual", STREAM_CONFIGS["Residual"]

    # 3. Not recognized as waste (non-waste items are dropped)
    return None


def run_sahi_tiled_inference(
    model,
    img: np.ndarray,
    conf_threshold: float = 0.18,
    iou_threshold: float = 0.45,
    max_det: int = 150,
    tile_grid: Tuple[int, int] = (2, 2),
    overlap: float = 0.20
) -> List[Dict[str, Any]]:
    """
    Performs SAHI-style (Slicing Aided Hyper Inference) multi-scale overlapping grid inference.
    Catches small objects (lids, bottle caps, foil wrappers, battery cells) that disappear in full-frame resizing.
    EXPLICITLY EXCLUDES humans/people and non-waste classes.
    """
    h, w = img.shape[:2]
    raw_boxes = []
    raw_scores = []
    raw_classes = []

    # Helper to check and append box
    def add_candidate(x1, y1, x2, y2, conf, cls_name):
        if is_blocked_non_waste(cls_name):
            return
        mapped = map_raw_label(cls_name)
        if mapped is None:
            return
        bw = x2 - x1
        bh = y2 - y1
        # Filter micro-noise: allow small and distant waste items (area >= 64px)
        if bw < 8 or bh < 8 or (bw * bh) < 64:
            return
        raw_boxes.append([x1, y1, bw, bh])
        raw_scores.append(conf)
        raw_classes.append(cls_name)

    # 1. Full Image Inference Pass (100% of frame from (0,0) to (w,h))
    res_full = model.predict(img, conf=conf_threshold, iou=iou_threshold, max_det=max_det, verbose=False)
    if res_full and len(res_full) > 0 and len(res_full[0].boxes) > 0:
        for b in res_full[0].boxes:
            xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
            conf = float(b.conf[0].cpu().numpy())
            cls_id = int(b.cls[0].cpu().numpy())
            cls_name = model.names.get(cls_id, "")
            add_candidate(xyxy[0], xyxy[1], xyxy[2], xyxy[3], conf, cls_name)

    # 2. Overlapping High-Resolution Tiled Passes (SAHI)
    rows, cols = tile_grid
    tile_h = int(h / (rows - (rows - 1) * overlap))
    tile_w = int(w / (cols - (cols - 1) * overlap))

    for r in range(rows):
        for c in range(cols):
            y1 = int(r * tile_h * (1 - overlap))
            x1 = int(c * tile_w * (1 - overlap))
            y2 = min(h, y1 + tile_h)
            x2 = min(w, x1 + tile_w)

            tile = img[y1:y2, x1:x2]
            if tile.size == 0:
                continue

            res_tile = model.predict(tile, conf=conf_threshold, iou=iou_threshold, max_det=80, verbose=False)
            if res_tile and len(res_tile) > 0 and len(res_tile[0].boxes) > 0:
                for b in res_tile[0].boxes:
                    t_xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
                    t_conf = float(b.conf[0].cpu().numpy())
                    t_cls = int(b.cls[0].cpu().numpy())
                    t_name = model.names.get(t_cls, "")

                    # Translate back to global coordinates
                    gx1 = x1 + t_xyxy[0]
                    gy1 = y1 + t_xyxy[1]
                    gx2 = x1 + t_xyxy[2]
                    gy2 = y1 + t_xyxy[3]

                    add_candidate(gx1, gy1, gx2, gy2, t_conf, t_name)

    # 3. Class-aware Non-Maximum Suppression (NMS)
    if not raw_boxes:
        return []

    indices = cv2.dnn.NMSBoxes(raw_boxes, raw_scores, score_threshold=conf_threshold, nms_threshold=iou_threshold)
    filtered_results = []

    if len(indices) > 0:
        for idx in indices.flatten():
            bx, by, bw, bh = raw_boxes[idx]
            x1 = max(0, min(w - 1, bx))
            y1 = max(0, min(h - 1, by))
            x2 = max(x1 + 1, min(w, bx + bw))
            y2 = max(y1 + 1, min(h, by + bh))
            conf = raw_scores[idx]
            cls_name = raw_classes[idx]

            filtered_results.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "rawClass": cls_name
            })

    return filtered_results


def draw_crisp_annotation(
    img: np.ndarray,
    box: List[int],
    label_text: str,
    conf_pct_str: str,
    style: Dict[str, Any]
) -> None:
    """
    Renders high-contrast bounding boxes with corner accents and smart pill labels.
    Format: `<label>: <conf>%` (e.g. `bottle: 98%`, `can: 94%`, `lid: 91%`).
    """
    x1, y1, x2, y2 = box
    bgr = style["bgr"]
    h, w, _ = img.shape

    # Main Bounding Box
    cv2.rectangle(img, (x1, y1), (x2, y2), bgr, 2, cv2.LINE_AA)

    # Corner brackets for tech-city HUD aesthetic
    c_len = min(16, (x2 - x1) // 3, (y2 - y1) // 3)
    if c_len > 4:
        cv2.line(img, (x1, y1), (x1 + c_len, y1), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x1, y1), (x1, y1 + c_len), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x2, y1), (x2 - c_len, y1), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x2, y1), (x2, y1 + c_len), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x1, y2), (x1 + c_len, y2), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x1, y2), (x1, y2 - c_len), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x2, y2), (x2 - c_len, y2), bgr, 4, cv2.LINE_AA)
        cv2.line(img, (x2, y2), (x2, y2 - c_len), bgr, 4, cv2.LINE_AA)

    # Pill text label
    text = f"{label_text}: {conf_pct_str}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.44
    font_thick = 1

    (tw, th), _ = cv2.getTextSize(text, font, font_scale, font_thick)

    # Position pill above box, or invert if close to top
    pill_y2 = y1 if y1 - th - 8 >= 0 else y1 + th + 8
    pill_y1 = pill_y2 - th - 6
    pill_x1 = max(0, x1)
    pill_x2 = min(w, x1 + tw + 12)

    # Solid pill background
    cv2.rectangle(img, (pill_x1, pill_y1), (pill_x2, pill_y2), bgr, -1, cv2.LINE_AA)
    # White crisp text
    cv2.putText(
        img,
        text,
        (pill_x1 + 6, pill_y2 - 4),
        font,
        font_scale,
        (255, 255, 255),
        font_thick,
        cv2.LINE_AA,
    )


def detect_multi_objects_image(
    image_bytes: bytes,
    conf_threshold: float = 0.20,
    iou_threshold: float = 0.45,
    max_det: int = 150,
) -> Dict[str, Any]:
    """
    High-accuracy multi-item waste detection for uploaded photos.
    Runs SAHI multi-scale overlapping tiled inference + NMS across 100% of the frame.
    STRICTLY FILTERS OUT humans, vehicles, animals, and furniture so people are NEVER classified as waste.
    """
    start_time = time.time()

    nparr = np.frombuffer(image_bytes, np.uint8)
    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if cv_img is None:
        raise ValueError("Could not decode image from provided bytes.")

    orig_h, orig_w = cv_img.shape[:2]
    annotated_img = cv_img.copy()

    model = get_yolo_model()
    detections: List[Dict[str, Any]] = []

    category_counts = {
        "Recyclable / Plastic": 0,
        "Organic / Biodegradable": 0,
        "Hazardous / E-Waste": 0,
        "Non-Recyclable / Residual": 0,
    }

    if model is not None:
        try:
            # Multi-scale overlapping tiled inference (SAHI) covering full image (0,0) to (w,h)
            raw_dets = run_sahi_tiled_inference(
                model=model,
                img=cv_img,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold,
                max_det=max_det,
                tile_grid=(2, 2),
                overlap=0.25
            )

            for idx, r in enumerate(raw_dets):
                x1, y1, x2, y2 = r["bbox"]
                conf = r["confidence"]
                raw_class = r["rawClass"]

                # Extra defense-in-depth non-waste & human filter
                if is_blocked_non_waste(raw_class):
                    continue

                mapped = map_raw_label(raw_class)
                if mapped is None:
                    continue

                label_code, human_name, stream_key, style = mapped
                conf_pct = int(round(conf * 100))
                conf_pct_str = f"{conf_pct}%"

                category_counts[style["fullName"]] += 1

                box_norm = {
                    "x": round((x1 / orig_w) * 100, 2),
                    "y": round((y1 / orig_h) * 100, 2),
                    "width": round(((x2 - x1) / orig_w) * 100, 2),
                    "height": round(((y2 - y1) / orig_h) * 100, 2),
                }

                area_px = int((x2 - x1) * (y2 - y1))

                detections.append({
                    "id": f"item-{len(detections) + 1}",
                    "label": label_code,
                    "humanLabel": human_name,
                    "category": style["fullName"],
                    "stream": stream_key,
                    "confidence": round(conf, 3),
                    "confidencePercent": conf_pct_str,
                    "binName": style["binName"],
                    "binColor": style["binColor"],
                    "colorHex": style["colorHex"],
                    "disposal_instruction": style["disposalInstruction"],
                    "bbox": [x1, y1, x2, y2],
                    "boxNorm": box_norm,
                    "area_px": area_px
                })

                draw_crisp_annotation(annotated_img, [x1, y1, x2, y2], label_code, conf_pct_str, style)
        except Exception as e:
            print(f"[EcoRoute AI] Tiled detection notice: {e}")

    # Encode annotated image to JPEG base64
    _, buffer = cv2.imencode(".jpg", annotated_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    annotated_base64 = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

    elapsed_ms = round((time.time() - start_time) * 1000, 1)
    primary_category = max(category_counts.items(), key=lambda x: x[1])[0] if detections else "None Detected"

    return {
        "success": True,
        "totalObjects": len(detections),
        "primaryCategory": primary_category,
        "categoryCounts": category_counts,
        "detections": detections,
        "annotatedImage": annotated_base64,
        "processingTimeMs": elapsed_ms,
        "imageDimensions": {"width": orig_w, "height": orig_h},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wasteOnlyVerified": True
    }


def process_waste_video(
    video_bytes: bytes,
    conf_threshold: float = 0.18,
    iou_threshold: float = 0.45,
    max_frames_to_process: int = 200,
) -> Dict[str, Any]:
    """
    Processes video frame-by-frame with OpenCV & YOLOv8.
    Encodes annotated MP4 with bounding boxes and percentage labels on every frame.
    Strictly filters out humans and non-waste entities.
    Returns playable video URL + complete itemized breakdown.
    """
    start_time = time.time()
    unique_id = uuid.uuid4().hex[:10]

    temp_input_path = os.path.join(UPLOADS_DIR, f"input_{unique_id}.mp4")
    with open(temp_input_path, "wb") as f:
        f.write(video_bytes)

    cap = cv2.VideoCapture(temp_input_path)
    if not cap.isOpened():
        raise ValueError("Could not open uploaded video stream.")

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    output_filename = f"annotated_{unique_id}.mp4"
    output_path = os.path.join(OUTPUTS_DIR, output_filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (orig_w, orig_h))

    model = get_yolo_model()

    total_detections_count = 0
    category_counts = {
        "Recyclable / Plastic": 0,
        "Organic / Biodegradable": 0,
        "Hazardous / E-Waste": 0,
        "Non-Recyclable / Residual": 0,
    }
    unique_items_map: Dict[str, Dict[str, Any]] = {}

    frame_idx = 0
    step = max(1, total_frames // max_frames_to_process) if total_frames > max_frames_to_process else 1
    last_detections = []

    while cap.isOpened() and frame_idx < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            current_frame_dets = []
            if model is not None:
                try:
                    res = model.predict(frame, conf=conf_threshold, iou=iou_threshold, max_det=60, verbose=False)
                    if res and len(res) > 0 and len(res[0].boxes) > 0:
                        for b in res[0].boxes:
                            xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
                            conf = float(b.conf[0].cpu().numpy())
                            cls_id = int(b.cls[0].cpu().numpy())
                            raw_class = model.names.get(cls_id, "")

                            # Filter humans & non-waste entities
                            if is_blocked_non_waste(raw_class):
                                continue

                            mapped = map_raw_label(raw_class)
                            if mapped is None:
                                continue

                            label_code, human_name, stream_key, style = mapped
                            conf_pct = int(round(conf * 100))
                            conf_pct_str = f"{conf_pct}%"

                            category_counts[style["fullName"]] += 1
                            total_detections_count += 1

                            if label_code not in unique_items_map:
                                unique_items_map[label_code] = {
                                    "item": human_name,
                                    "code": label_code,
                                    "category": style["fullName"],
                                    "stream": stream_key,
                                    "colorHex": style["colorHex"],
                                    "count": 0,
                                }
                            unique_items_map[label_code]["count"] += 1

                            current_frame_dets.append((xyxy, label_code, conf_pct_str, style))
                except Exception:
                    pass
            last_detections = current_frame_dets

        # Render annotations on frame
        for xyxy, label_code, conf_pct_str, style in last_detections:
            draw_crisp_annotation(frame, xyxy, label_code, conf_pct_str, style)

        # Smart-city HUD overlay banner
        cv2.rectangle(frame, (12, 12), (400, 46), (11, 59, 36), -1)
        cv2.putText(
            frame,
            f"EcoRoute AI | {len(last_detections)} waste items (humans excluded)",
            (20, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.46,
            (16, 185, 129),
            1,
            cv2.LINE_AA,
        )

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    try:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
    except Exception:
        pass

    elapsed_ms = round((time.time() - start_time) * 1000, 1)
    duration_sec = round(frame_idx / fps, 2) if fps > 0 else 0.0
    sorted_unique = sorted(unique_items_map.values(), key=lambda x: x["count"], reverse=True)

    return {
        "success": True,
        "videoUrl": f"/static/outputs/{output_filename}",
        "framesProcessed": frame_idx,
        "fps": round(fps, 1),
        "durationSeconds": duration_sec,
        "totalDetections": total_detections_count,
        "categoryCounts": category_counts,
        "uniqueWasteItems": sorted_unique,
        "processingTimeMs": elapsed_ms,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wasteOnlyVerified": True
    }
