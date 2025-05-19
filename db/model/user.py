import enum
from sqlalchemy import Column, String, Enum, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .mixins import Timestamp
from ..db_setup import Base

class Role(enum.Enum):
    admin = "admin"
    staff = "staff"
    user = "user"

class User(Timestamp, Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashed password
    role = Column(Enum(Role), nullable=False)
    roleID = Column(String(10), nullable=False)
    displayName = Column(String(100), nullable=False)
    photoURL = Column(String(255), nullable=True)
    pmpRestriction = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    shortcuts = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=False)

    profile = relationship("Profile", back_populates="owner", uselist=False)