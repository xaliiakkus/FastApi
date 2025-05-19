# api/menuitems/menuitems.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.db_setup import get_db
from api.crud import get_menuitems, get_menuitem, create_menuitem, update_menuitem, delete_menuitem
from db.model.menuitem import MenuItem
from routes.auth import verify_token

router = APIRouter(prefix="/menuitems", tags=["menuitems"])

class MenuItemBase(BaseModel):
    menuDisplayname: str
    menuurl: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    translate: Optional[str] = None
    translateKey: Optional[str] = None
    children: Optional[List[dict]] = None

class MenuItemCreate(MenuItemBase):
    menuID: str

class MenuItemUpdate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    menuID: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[MenuItemResponse])
def get_menuitems_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_menuitems(db, skip, limit)

@router.post("/", response_model=MenuItemResponse)
def create_menuitem_endpoint(
    menuitem: MenuItemCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_menuitem = create_menuitem(db, menuitem.dict())
    return db_menuitem

@router.get("/{menuID}", response_model=MenuItemResponse)
def get_menuitem_endpoint(
    menuID: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_menuitem = get_menuitem(db, menuID)
    if not db_menuitem:
        raise HTTPException(status_code=404, detail="MenuItem not found")
    return db_menuitem

@router.put("/{menuID}", response_model=MenuItemResponse)
def update_menuitem_endpoint(
    menuID: str,
    menuitem: MenuItemUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_menuitem = update_menuitem(db, menuID, menuitem.dict(exclude_unset=True))
    if not db_menuitem:
        raise HTTPException(status_code=404, detail="MenuItem not found")
    return db_menuitem

@router.delete("/{menuID}", response_model=dict)
def delete_menuitem_endpoint(
    menuID: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_menuitem(db, menuID):
        raise HTTPException(status_code=404, detail="MenuItem not found")
    return {"message": "MenuItem deleted"}