# models/role.py
from sqlalchemy import Column, String, JSON
from .mixins import Timestamp
from ..db_setup import Base

class RoleList(Timestamp, Base):
    __tablename__ = "rolelist"

    id = Column(String(10), primary_key=True, index=True)
    RoleName = Column(String(50), nullable=False)
    menuitems = Column(JSON, nullable=True)