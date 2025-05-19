# models/company.py
from sqlalchemy import Column, String
from .mixins import Timestamp
from ..db_setup import Base

class Company(Timestamp, Base):
    __tablename__ = "companies"

    CompanyId = Column(String(10), primary_key=True, index=True)
    CompanyName = Column(String(100), nullable=False)
    OwnerId = Column(String(50), nullable=True)