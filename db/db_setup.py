from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "postgresql://fastapi_hd2t_user:BV6elm9ESj6wBNP3va9I9u95PG6SdkMO@dpg-cvttq6qdbo4c739aurj0-a.oregon-postgres.render.com/fastapi_hd2t" # Example for PostgreSQL, change as needed
# DATABASE_URL = "postgresql://postgres:1453@localhost:3000/postgres" # Example for SQLite, change as needed
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, future=True , autoflush=False, bind=engine)
Base = declarative_base()

try:
    with engine.connect() as connection:
        print("Bağlantı başarılı!")
except Exception as e:
    print(f"Bağlantı hatası: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()