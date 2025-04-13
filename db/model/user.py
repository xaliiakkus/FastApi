import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum,Text, Float, Date,String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .mixins import Timestamp
from ..db_setup import Base


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Timestamp,Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(Enum(Role))
    password = Column(String(100))
    # users ile profile tablosu arasında ilişki kuruyoruz
    profile =relationship("Profile", back_populates="owner", uselist=False)

class Profile(Timestamp,Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    fist_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    bio= Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    ## users tablosuna gidip bakacak id eşit olanı alacak
    ## foreign key ile ilişkilendiriyoruz
    user_id= Column(Integer, ForeignKey("users.id"), nullable=False)
    # kullanıcı tablosu ile ilişki kuruyoruz
    owner = relationship("User", back_populates="profile")