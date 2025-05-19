# models/station_summary.py
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from .mixins import Timestamp
from ..db_setup import Base

class StationSummary(Timestamp, Base):
    __tablename__ = "station_summaries"

    id = Column(String(10), primary_key=True, index=True)
    supplyId = Column(Integer, nullable=True)
    accountId = Column(Integer, nullable=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    taxOffice = Column(String(100), nullable=True)
    taxNumber = Column(String(20), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    phone = Column(String(20), nullable=True)
    order = Column(Integer, nullable=True)
    city = Column(String(100), nullable=True)
    PumperId = Column(Integer, nullable=True)
    CompanyId = Column(String(10), nullable=True)
    status = Column(String(20), nullable=True)
    Dispatchers = Column(JSON, nullable=True)  # Store nested dispatchers as JSON