# models/notification.py
from sqlalchemy import Column, String, Integer, Float, DateTime
from .mixins import Timestamp
from ..db_setup import Base

class Notification(Timestamp, Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    company_id = Column(Integer, nullable=True)
    station_id = Column(Integer, nullable=True)
    dispatcher_id = Column(Integer, nullable=True)
    transfer_batch_total = Column(Float, nullable=True)
    transfer_grand_total_start = Column(Float, nullable=True)
    transfer_create_date = Column(DateTime, nullable=True)
    company_name = Column(String(100), nullable=True)
    station_name = Column(String(100), nullable=True)
    dispatcher_name = Column(String(100), nullable=True)