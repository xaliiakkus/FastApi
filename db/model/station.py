# models/station.py
from sqlalchemy import Column, String, Float, Integer
from .mixins import Timestamp
from ..db_setup import Base

class StationItem(Timestamp, Base):
    __tablename__ = "stations"

    id = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    taxOffice = Column(String(100), nullable=True)
    taxNumber = Column(String(20), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    phone = Column(String(20), nullable=True)
    order = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)
    PumperId = Column(Integer, nullable=True)
    city = Column(String(100), nullable=True)
    CompanyId = Column(String(10), nullable=True)