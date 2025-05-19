# api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt
import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from ..db.db_setup import get_db
from  ..api.crud import get_user_by_email, hash_password
from ..db.model.user import User as UserModel

router = APIRouter()

SECRET_KEY = "secret_key"  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class LoginData(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    roleID: str
    displayName: str

    class Config:
        from_attributes = True

def create_token(user: UserModel) -> str:
    payload: dict[str, str | int | float | None] = {
        "user_id": str(user.id),
        "email": user.email,
        "role": str(user.role.value),
        "roleID": str(user.roleID),
        "displayName": user.displayName,
        "exp": int((datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())
    } # type: ignore
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def verify_token(token: str = Depends(oauth2_scheme)) -> dict: # type: ignore
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=dict, tags=["auth"])
def login(data: LoginData, db: Session = Depends(get_db)):# type: ignore
    user = get_user_by_email(db, data.email)# type: ignore
    if not user or not verify_password(data.password, user.password):# type: ignore
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "roleID": user.roleID,
            "displayName": user.displayName
        }
    }# type: ignore