from typing import Optional, List
from fastapi import Path, Query,APIRouter
from pydantic import BaseModel


router = APIRouter()

users= []
class User(BaseModel):
    name: str
    is_active: Optional[bool]= True
    email: str
    password: str



@router.get("/users" ,response_model=List[User])
async def getUsers():
 return users

@router.post("/users")
async def CreateUsers(user:User):
    users.append(user)
    return {"message": "User Created"}

@router.get("/users/{id}")
async def getUser(
    id: int = Path(..., description="The ID of the user to get", gt=0),
     q: Optional[str] = Query(None, min_length=3, max_length=50, description="Query string for searching users")
 ): return {'users':users[id], 'query':q}      



 