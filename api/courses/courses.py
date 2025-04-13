
from fastapi import APIRouter

router = APIRouter()




@router.get("/courses")
def read_courses():
    return {"courses": []}


@router.post("/courses")
def create_courses_api():
    return {"courses": []}


@router.get("/courses/{id}")
def read_course():
    return {"courses": []}


@router.patch("/courses/{id}")
def update_course():
    return {"courses": []}


@router.delete("/courses/{id}")
def delete_course():
    return {"courses": []}



@router.get("/courses/{id}/sections")
def read_course_section():
    return {"courses": []}

