from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import list_notifications, mark_notification_read, clear_all_notifications, create_notification

router = APIRouter(prefix="", tags=["Notifications & Alerts"])


class NewNotificationPayload(BaseModel):
    title: str
    message: str
    level: str = "info"
    bin_id: Optional[str] = None
    vehicle_id: Optional[str] = None


@router.get("/notifications")
@router.get("/api/notifications")
async def get_notifications():
    """Returns active operational notifications and alerts."""
    return list_notifications()


@router.post("/notifications/{notif_id}/read")
@router.post("/api/notifications/{notif_id}/read")
async def mark_read(notif_id: str):
    """Marks a single notification as read."""
    success = mark_notification_read(notif_id)
    return {"success": success}


@router.post("/notifications/clear-all")
@router.post("/api/notifications/clear-all")
async def clear_all():
    """Marks all operational alerts as read."""
    success = clear_all_notifications()
    return {"success": success}


@router.post("/notifications")
@router.post("/api/notifications")
async def create_new_notification(payload: NewNotificationPayload):
    """Creates a new notification."""
    notif = create_notification(
        title=payload.title,
        message=payload.message,
        level=payload.level,
        bin_id=payload.bin_id,
        vehicle_id=payload.vehicle_id
    )
    return {"success": True, "notification": notif}
