# api/vehicles/vehicles.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_vehicles, get_vehicle, create_vehicle, update_vehicle, delete_vehicle
from ...models.vehicle import Vehicle
from ..auth import verify_token

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

class VehicleBase(BaseModel):
    OID: Optional[str] = None
    Company: Optional[str] = None
    CardName: Optional[str] = None
    MonthLimit: Optional[float] = None
    MontTransfer: Optional[float] = None
    Totaltransfer: Optional[float] = None
    CardTypeID: Optional[str] = None
    RfId: Optional[str] = None
    IsActive: Optional[bool] = None

class VehicleCreate(VehicleBase):
    VehicleId: str

class VehicleUpdate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    VehicleId: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_vehicles(db, skip, limit)

@router.post("/", response_model=VehicleResponse)
def create_vehicle_endpoint(
    vehicle: VehicleCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_vehicle = create_vehicle(db, vehicle.dict())
    return db_vehicle

@router.get("/{VehicleId}", response_model=VehicleResponse)
def get_vehicle_endpoint(
    VehicleId: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_vehicle = get_vehicle(db, VehicleId)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@router.put("/{VehicleId}", response_model=VehicleResponse)
def update_vehicle_endpoint(
    VehicleId: str,
    vehicle: VehicleUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_vehicle = update_vehicle(db, VehicleId, vehicle.dict(exclude_unset=True))
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@router.delete("/{VehicleId}", response_model=dict)
def delete_vehicle_endpoint(
    VehicleId: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_vehicle(db, VehicleId):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted"}