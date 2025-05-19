# api/notifications/notifications.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.db_setup import get_db
from crud.crud import get_notifications, get_notification, create_notification, update_notification, delete_notification
from db.model.notification import Notification
from routes.auth import verify_token
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationBase(BaseModel):
    company_id: Optional[int] = None
    station_id: Optional[int] = None
    dispatcher_id: Optional[int] = None
    transfer_batch_total: Optional[float] = None
    transfer_grand_total_start: Optional[float] = None
    transfer_create_date: Optional[datetime] = None
    company_name: Optional[str] = None
    station_name: Optional[str] = None
    dispatcher_name: Optional[str] = None

class NotificationCreate(NotificationBase):
    id: str

class NotificationUpdate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
def get_notifications_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_notifications(db, skip, limit)

@router.post("/", response_model=NotificationResponse)
def create_notification_endpoint(
    notification: NotificationCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_notification = create_notification(db, notification.dict())
    return db_notification

@router.get("/{id}", response_model=NotificationResponse)
def get_notification_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_notification = get_notification(db, id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification

@router.put("/{id}", response_model=NotificationResponse)
def update_notification_endpoint(
    id: str,
    notification: NotificationUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_notification = update_notification(db, id, notification.dict(exclude_unset=True))
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification

@router.delete("/{id}", response_model=dict)
def delete_notification_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_notification(db, id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}