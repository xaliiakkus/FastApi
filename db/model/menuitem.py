# models/menuitem.py
from sqlalchemy import Column, String, JSON
from .mixins import Timestamp
from ..db_setup import Base

class MenuItem(Timestamp, Base):
    __tablename__ = "menuitems"

    menuID = Column(String(10), primary_key=True, index=True)
    menuDisplayname = Column(String(100), nullable=False)
    menuurl = Column(String(255), nullable=True)
    title = Column(String(100), nullable=True)
    subtitle = Column(String(100), nullable=True)
    type = Column(String(50), nullable=True)
    icon = Column(String(100), nullable=True)
    translate = Column(String(100), nullable=True)
    translateKey = Column(String(100), nullable=True)
    children = Column(JSON, nullable=True)