# api/transfers/transfers.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_transfers, get_transfer, create_transfer, update_transfer, delete_transfer
from ...models.transfer import TransfersDispatcher
from ..auth import verify_token
from datetime import datetime

router = APIRouter(prefix="/transfers", tags=["transfers"])

class TransferBase(BaseModel):
    OID: Optional[int] = None
    CompanyId: Optional[str] = None
    DispatcherId: Optional[str] = None
    VehicleId: Optional[str] = None
    Status: Optional[str] = None
    DateRealized: Optional[datetime] = None
    CreateDate: Optional[int] = None
    GrandTotalStart: Optional[float] = None
    BatchTotal: Optional[float] = None
    Type: Optional[str] = None
    BatchPrice: Optional[float] = None

class TransferCreate(TransferBase):
    id: str

class TransferUpdate(TransferBase):
    pass

class TransferResponse(TransferBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TransferResponse])
def get_transfers_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_transfers(db, skip, limit)

@router.post("/", response_model=TransferResponse)
def create_transfer_endpoint(
    transfer: TransferCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_transfer = create_transfer(db, transfer.dict())
    return db_transfer

@router.get("/{id}", response_model=TransferResponse)
def get_transfer_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_transfer = get_transfer(db, id)
    if not db_transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return db_transfer

@router.put("/{id}", response_model=TransferResponse)
def update_transfer_endpoint(
    id: str,
    transfer: TransferUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_transfer = update_transfer(db, id, transfer.dict(exclude_unset=True))
    if not db_transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return db_transfer

@router.delete("/{id}", response_model=dict)
def delete_transfer_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_transfer(db, id):
        raise HTTPException(status_code=404, detail="Transfer not found")
    return {"message": "Transfer deleted"}