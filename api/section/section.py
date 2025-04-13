from fastapi import APIRouter

router = APIRouter()



@router.get("/section/{id}")
def read_section():
    return {"courses": []}

@router.get("/section/{id}/content-blocks")
def read_section():
    return {"courses": []}



@router.get("/content-blocks/{id}")
def read_section():
    return {"courses": []}
