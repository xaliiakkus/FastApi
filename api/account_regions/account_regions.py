# api/account_regions/account_regions.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_account_regions, get_account_region, create_account_region, update_account_region, delete_account_region
from ...models.account_region import AccountRegion
from ..auth import verify_token

router = APIRouter(prefix="/account-regions", tags=["account_regions"])

class AccountRegionBase(BaseModel):
    name: str

class AccountRegionCreate(AccountRegionBase):
    Id: int

class AccountRegionUpdate(AccountRegionBase):
    pass

class AccountRegionResponse(AccountRegionBase):
    Id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AccountRegionResponse])
def get_account_regions_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_account_regions(db, skip, limit)

@router.post("/", response_model=AccountRegionResponse)
def create_account_region_endpoint(
    region: AccountRegionCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_region = create_account_region(db, region.dict())
    return db_region

@router.get("/{Id}", response_model=AccountRegionResponse)
def get_account_region_endpoint(
    Id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_region = get_account_region(db, Id)
    if not db_region:
        raise HTTPException(status_code=404, detail="Account region not found")
    return db_region

@router.put("/{Id}", response_model=AccountRegionResponse)
def update_account_region_endpoint(
    Id: int,
    region: AccountRegionUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_region = update_account_region(db, Id, region.dict(exclude_unset=True))
    if not db_region:
        raise HTTPException(status_code=404, detail="Account region not found")
    return db_region

@router.delete("/{Id}", response_model=dict)
def delete_account_region_endpoint(
    Id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_account_region(db, Id):
        raise HTTPException(status_code=404, detail="Account region not found")
    return {"message": "Account region deleted"}