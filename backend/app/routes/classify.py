import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from app.models.schemas import ClassifyResponse
from app.services.yolo_service import analyze_waste_image

router = APIRouter(prefix="/classify-waste", tags=["Computer Vision Waste Segregation"])

@router.post("", response_model=ClassifyResponse)
async def classify_waste(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),
):
    """
    Classify a waste item image using YOLO computer vision.
    Accepts direct image file upload (multipart/form-data) or Base64 data URL string.
    Returns detected item name, confidence score, bounding box, and color-coded disposal guidance.
    """
    image_bytes = None

    if file is not None:
        try:
            image_bytes = await file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")
    elif image_data is not None:
        try:
            # Handle data:image/jpeg;base64,... header
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {e}")
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' upload or 'image_data' base64 string must be provided."
        )

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image payload received.")

    try:
        response = analyze_waste_image(image_bytes)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")
