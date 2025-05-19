
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.db_setup import get_db
from api.crud.crud import get_users, get_user, create_user, update_user, delete_user
from db.model.user import User as UserModel
from routes.auth import verify_token

router = APIRouter(prefix="/users", tags=["users"])

class UserBase(BaseModel):
    email: str
    role: str
    roleID: str
    displayName: str
    photoURL: Optional[str] = None
    pmpRestriction: Optional[dict] = None
    settings: Optional[dict] = None
    shortcuts: Optional[List[str]] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
def get_users_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return get_users(db, skip, limit)

@router.post("/", response_model=UserResponse)
def create_user_endpoint(
    user: UserCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    user_data = user.dict()
    user_data["id"] = str(uuid.uuid4())  # Generate unique ID
    db_user = create_user(db, user_data)
    return db_user

@router.get("/{id}", response_model=UserResponse)
def get_user_endpoint(
    id: str = Path(..., description="The ID of the user to get"),
    q: Optional[str] = Query(None, min_length=3, max_length=50, description="Query string for searching users"),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    db_user = get_user(db, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{id}", response_model=UserResponse)
def update_user_endpoint(
    id: str,
    user: UserUpdate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_user = update_user(db, id, user.dict(exclude_unset=True))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{id}", response_model=dict)
def delete_user_endpoint(
    id: str,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if not delete_user(db, id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}