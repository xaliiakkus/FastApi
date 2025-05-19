# models/vehicle.py
from sqlalchemy import Column, String, Float, Boolean
from .mixins import Timestamp
from ..db_setup import Base

class Vehicle(Timestamp, Base):
    __tablename__ = "vehicles"

    VehicleId = Column(String(10), primary_key=True, index=True)
    OID = Column(String(10), nullable=True)
    Company = Column(String(100), nullable=True)
    CardName = Column(String(100), nullable=True)
    MonthLimit = Column(Float, nullable=True)
    MontTransfer = Column(Float, nullable=True)
    Totaltransfer = Column(Float, nullable=True)
    CardTypeID = Column(String(50), nullable=True)
    RfId = Column(String(50), nullable=True)
    IsActive = Column(Boolean, nullable=True)