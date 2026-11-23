import base64
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.services.yolo_service import detect_multi_objects_image, process_waste_video

router = APIRouter(prefix="", tags=["Computer Vision Waste & Video Detection"])

@router.post("/detect/image")
@router.post("/detect-image")
@router.post("/api/detect-image")
async def detect_image_endpoint(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),
):
    """
    High-Accuracy Multi-Item Waste Detection (SAHI-style Overlapping Tiled YOLOv8).
    Detects bottles, cans, lids, foil, tubes, brushes, organic scraps, and e-waste.
    Returns:
    - Bounding boxes [x1, y1, x2, y2]
    - Normalized coordinates, pixel area, disposal instructions
    - Stream breakdown (Recyclable, Organic, Hazardous, Residual)
    - Base64 annotated image with crisp bounding boxes & pill labels
    """
    image_bytes = None

    if file is not None:
        try:
            image_bytes = await file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read image file: {e}")
    elif image_data is not None:
        try:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {e}")
    else:
        raise HTTPException(
            status_code=400,
            detail="Either an image 'file' upload or 'image_data' base64 string must be provided."
        )

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image received.")

    try:
        result = detect_multi_objects_image(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-object detection error: {e}")


@router.post("/detect/video")
@router.post("/detect-video")
@router.post("/api/detect-video")
async def detect_video_endpoint(
    file: UploadFile = File(...)
):
    """
    Video Detection Endpoint using OpenCV + YOLOv8.
    Processes uploaded .mp4 / .avi / .mov / .webm videos frame-by-frame,
    draws color-coded bounding boxes and <item>: XX% pill tags on every frame,
    and returns playable MP4 video URL + item breakdown.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No video file selected.")

    valid_extensions = (".mp4", ".avi", ".mov", ".webm", ".mkv")
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format. Allowed: {', '.join(valid_extensions)}"
        )

    try:
        video_bytes = await file.read()
        if len(video_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded video file is empty.")

        result = process_waste_video(video_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video detection processing error: {e}")


@router.post("/classify-waste")
@router.post("/api/classify-waste")
async def legacy_classify_waste(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),
):
    """Backward-compatible single/primary item endpoint."""
    res = await detect_image_endpoint(file=file, image_data=image_data)
    detections = res.get("detections", [])
    primary = detections[0] if detections else None

    return {
        "success": True,
        "item": primary,
        "totalObjects": len(detections),
        "detections": detections,
        "categoryCounts": res.get("categoryCounts", {}),
        "annotatedImage": res.get("annotatedImage"),
        "processingTimeMs": res.get("processingTimeMs", 0),
        "timestamp": res.get("timestamp"),
        "message": "Detection completed successfully. Non-waste and human subjects are strictly excluded."
    }
