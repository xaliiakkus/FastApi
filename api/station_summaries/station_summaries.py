# api/station_summaries/station_summaries.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_station_summaries, get_station_summary, create_station_summary, update_station_summary, delete_station_summary
from ...models.station_summary import StationSummary
from ..auth import verify_token

router = APIRouter(prefix="/station-summaries", tags=["station_summaries"])

class StationSummaryBase(BaseModel):
    supplyId: Optional[int] = None
    accountId: Optional[int] = None
    name: str
    address: Optional[str] = None
    taxOffice: Optional[str] = None
    taxNumber: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    phone: Optional[str] = None
    order: Optional[int] = None
    city: Optional[str] = None
    PumperId: Optional[int] = None
    CompanyId: Optional[str] = None
    status: Optional[str] = None
    Dispatchers: Optional[List[dict]] = None

class StationSummaryCreate(StationSummaryBase):
    id: str

class StationSummaryUpdate(StationSummaryBase):
    pass

class StationSummaryResponse(StationSummaryBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[StationSummaryResponse])
def get_station_summaries_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_station_summaries(db, skip, limit)

@router.post("/", response_model=StationSummaryResponse)
def create_station_summary_endpoint(
    summary: StationSummaryCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_summary = create_station_summary(db, summary.dict())
    return db_summary

@router.get("/{id}", response_model=StationSummaryResponse)
def get_station_summary_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_summary = get_station_summary(db, id)
    if not db_summary:
        raise HTTPException(status_code=404, detail="Station summary not found")
    return db_summary

@router.put("/{id}", response_model=StationSummaryResponse)
def update_station_summary_endpoint(
    id: str,
    summary: StationSummaryUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_summary = update_station_summary(db, id, summary.dict(exclude_unset=True))
    if not db_summary:
        raise HTTPException(status_code=404, detail="Station summary not found")
    return db_summary

@router.delete("/{id}", response_model=dict)
def delete_station_summary_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_station_summary(db, id):
        raise HTTPException(status_code=404, detail="Station summary not found")
    return {"message": "Station summary deleted"}