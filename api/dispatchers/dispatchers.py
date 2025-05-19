# api/dispatchers/dispatchers.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_dispatchers, get_dispatcher, create_dispatcher, update_dispatcher, delete_dispatcher
from ...models.dispatcher import Dispatcher
from ..auth import verify_token
from datetime import datetime

router = APIRouter(prefix="/dispatchers", tags=["dispatchers"])

class DispatcherBase(BaseModel):
    IMEI: Optional[str] = None
    StationId: Optional[int] = None
    DispatcherName: str
    LastUpdateDate: Optional[datetime] = None
    GrandTotal: Optional[float] = None
    K: Optional[str] = None
    isActive: Optional[int] = None
    DaviceId: Optional[str] = None
    Version: Optional[datetime] = None
    Tell: Optional[int] = None
    City: Optional[str] = None
    PName: Optional[str] = None
    District: Optional[str] = None
    PumpModel: Optional[int] = None
    isNotificationMailActive: Optional[str] = None
    CompanyId: Optional[str] = None

class DispatcherCreate(DispatcherBase):
    id: int

class DispatcherUpdate(DispatcherBase):
    pass

class DispatcherResponse(DispatcherBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[DispatcherResponse])
def get_dispatchers_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_dispatchers(db, skip, limit)

@router.post("/", response_model=DispatcherResponse)
def create_dispatcher_endpoint(
    dispatcher: DispatcherCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_dispatcher = create_dispatcher(db, dispatcher.dict())
    return db_dispatcher

@router.get("/{id}", response_model=DispatcherResponse)
def get_dispatcher_endpoint(
    id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_dispatcher = get_dispatcher(db, id)
    if not db_dispatcher:
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    return db_dispatcher

@router.put("/{id}", response_model=DispatcherResponse)
def update_dispatcher_endpoint(
    id: int,
    dispatcher: DispatcherUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_dispatcher = update_dispatcher(db, id, dispatcher.dict(exclude_unset=True))
    if not db_dispatcher:
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    return db_dispatcher

@router.delete("/{id}", response_model=dict)
def delete_dispatcher_endpoint(
    id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_dispatcher(db, id):
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    return {"message": "Dispatcher deleted"}