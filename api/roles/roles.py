from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...db.db_setup import get_db
from ...db.model.role import RoleList 
from ...api.crud import get_roles, get_role, create_role, update_role, delete_role
from ...db.db_setup import get_db
from ...routes.auth import verify_token

router = APIRouter(prefix="/roles", tags=["roles"])

class RoleBase(BaseModel):
    RoleName: str
    menuitems: Optional[List[str]] = None

class RoleCreate(RoleBase):
    id: str

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[RoleResponse])
def get_roles_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_roles(db, skip, limit)

@router.post("/", response_model=RoleResponse)
def create_role_endpoint(
    role: RoleCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_role = create_role(db, role.dict())
    return db_role

@router.get("/{id}", response_model=RoleResponse)
def get_role_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_role = get_role(db, id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/{id}", response_model=RoleResponse)
def update_role_endpoint(
    id: str,
    role: RoleUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_role = update_role(db, id, role.dict(exclude_unset=True))
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/{id}", response_model=dict)
def delete_role_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_role(db, id):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted"}