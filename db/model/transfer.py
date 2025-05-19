# models/transfer.py
from sqlalchemy import Column, String, Integer, Float, DateTime
from .mixins import Timestamp
from ..db_setup import Base

class TransfersDispatcher(Timestamp, Base):
    __tablename__ = "transfers"

    id = Column(String(10), primary_key=True, index=True)
    OID = Column(Integer, nullable=True)
    CompanyId = Column(String(10), nullable=True)
    DispatcherId = Column(String(10), nullable=True)
    VehicleId = Column(String(10), nullable=True)
    Status = Column(String(20), nullable=True)
    DateRealized = Column(DateTime, nullable=True)
    CreateDate = Column(Integer, nullable=True)
    GrandTotalStart = Column(Float, nullable=True)
    BatchTotal = Column(Float, nullable=True)
    Type = Column(String(50), nullable=True)
    BatchPrice = Column(Float, nullable=True)