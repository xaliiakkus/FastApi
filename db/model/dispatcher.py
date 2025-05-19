# models/dispatcher.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from .mixins import Timestamp
from ..db_setup import Base

class Dispatcher(Timestamp, Base):
    __tablename__ = "dispatchers"

    id = Column(Integer, primary_key=True, index=True)
    IMEI = Column(String(50), nullable=True)
    StationId = Column(Integer, nullable=True)
    DispatcherName = Column(String(100), nullable=False)
    LastUpdateDate = Column(DateTime, nullable=True)
    GrandTotal = Column(Float, nullable=True)
    K = Column(String(50), nullable=True)
    isActive = Column(Integer, nullable=True)
    DaviceId = Column(String(50), nullable=True)
    Version = Column(DateTime, nullable=True)
    Tell = Column(Integer, nullable=True)
    City = Column(String(100), nullable=True)
    PName = Column(String(100), nullable=True)
    District = Column(String(100), nullable=True)
    PumpModel = Column(Integer, nullable=True)
    isNotificationMailActive = Column(String(100), nullable=True)
    CompanyId = Column(String(10), nullable=True)