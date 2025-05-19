# api/supply_regions/supply_regions.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_supply_regions, get_supply_region, create_supply_region, update_supply_region, delete_supply_region
from ...models.supply_region import SupplyRegion
from ..auth import verify_token

router = APIRouter(prefix="/supply-regions", tags=["supply_regions"])

class SupplyRegionBase(BaseModel):
    name: str

class SupplyRegionCreate(SupplyRegionBase):
    Id: int

class SupplyRegionUpdate(SupplyRegionBase):
    pass

class SupplyRegionResponse(SupplyRegionBase):
    Id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[SupplyRegionResponse])
def get_supply_regions_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_supply_regions(db, skip, limit)

@router.post("/", response_model=SupplyRegionResponse)
def create_supply_region_endpoint(
    region: SupplyRegionCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_region = create_supply_region(db, region.dict())
    return db_region

@router.get("/{Id}", response_model=SupplyRegionResponse)
def get_supply_region_endpoint(
    Id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_region = get_supply_region(db, Id)
    if not db_region:
        raise HTTPException(status_code=404, detail="Supply region not found")
    return db_region

@router.put("/{Id}", response_model=SupplyRegionResponse)
def update_supply_region_endpoint(
    Id: int,
    region: SupplyRegionUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_region = update_supply_region(db, Id, region.dict(exclude_unset=True))
    if not db_region:
        raise HTTPException(status_code=404, detail="Supply region not found")
    return db_region

@router.delete("/{Id}", response_model=dict)
def delete_supply_region_endpoint(
    Id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_supply_region(db, Id):
        raise HTTPException(status_code=404, detail="Supply region not found")
    return {"message": "Supply region deleted"}