
from fastapi import FastAPI
from api.users.users import router as users_router
from api.courses.courses import router as courses_router
from api.section.section import router as sections_router
from db.db_setup import engine
from db.model import course, user

# from db.db import engine
user.Base.metadata.create_all(bind=engine)
course.Base.metadata.create_all(bind=engine)




app = FastAPI()


app.include_router(users_router)
app.include_router(courses_router)
app.include_router(sections_router)