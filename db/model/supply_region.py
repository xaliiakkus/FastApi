# models/supply_region.py
from sqlalchemy import Column, Integer, String
from .mixins import Timestamp
from ..db_setup import Base

class SupplyRegion(Timestamp, Base):
    __tablename__ = "supply_regions"

    Id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)