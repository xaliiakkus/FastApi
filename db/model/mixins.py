# models/mixins.py (assumed from previous code)
from sqlalchemy import Column, DateTime
from datetime import datetime

class Timestamp:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)