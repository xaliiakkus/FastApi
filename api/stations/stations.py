# api/stations/stations.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_stations, get_station, create_station, update_station, delete_station
from ...models.station import StationItem
from ..auth import verify_token

router = APIRouter(prefix="/stations", tags=["stations"])

class StationBase(BaseModel):
    name: str
    address: Optional[str] = None
    taxOffice: Optional[str] = None
    taxNumber: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    phone: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None
    PumperId: Optional[int] = None
    city: Optional[str] = None
    CompanyId: Optional[str] = None

class StationCreate(StationBase):
    id: str

class StationUpdate(StationBase):
    pass

class StationResponse(StationBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[StationResponse])
def get_stations_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_stations(db, skip, limit)

@router.post("/", response_model=StationResponse)
def create_station_endpoint(
    station: StationCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_station = create_station(db, station.dict())
    return db_station

@router.get("/{id}", response_model=StationResponse)
def get_station_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_station = get_station(db, id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station

@router.put("/{id}", response_model=StationResponse)
def update_station_endpoint(
    id: str,
    station: StationUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_station = update_station(db, id, station.dict(exclude_unset=True))
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station

@router.delete("/{id}", response_model=dict)
def delete_station_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_station(db, id):
        raise HTTPException(status_code=404, detail="Station not found")
    return {"message": "Station deleted"}