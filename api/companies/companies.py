# api/companies/companies.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db_setup import get_db
from ...crud import get_companies, get_company, create_company, update_company, delete_company
from ...models.company import Company
from ..auth import verify_token

router = APIRouter(prefix="/companies", tags=["companies"])

class CompanyBase(BaseModel):
    CompanyName: str
    OwnerId: Optional[str] = None

class CompanyCreate(CompanyBase):
    CompanyId: str

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    CompanyId: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CompanyResponse])
def get_companies_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_companies(db, skip, limit)

@router.post("/", response_model=CompanyResponse)
def create_company_endpoint(
    company: CompanyCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_company = create_company(db, company.dict())
    return db_company

@router.get("/{CompanyId}", response_model=CompanyResponse)
def get_company_endpoint(
    CompanyId: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_company = get_company(db, CompanyId)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{CompanyId}", response_model=CompanyResponse)
def update_company_endpoint(
    CompanyId: str,
    company: CompanyUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_company = update_company(db, CompanyId, company.dict(exclude_unset=True))
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.delete("/{CompanyId}", response_model=dict)
def delete_company_endpoint(
    CompanyId: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_company(db, CompanyId):
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted"}