# models/account_region.py
from sqlalchemy import Column, Integer, String
from .mixins import Timestamp
from ..db_setup import Base

class AccountRegion(Timestamp, Base):
    __tablename__ = "account_regions"

    Id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)