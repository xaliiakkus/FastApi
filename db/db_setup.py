from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "postgresql://postgres:1453@localhost:5432/postgres" # Example for SQLite, change as needed
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