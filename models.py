from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    project_id = Column(String, nullable=True)
    env = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    locktime = Column(DateTime, nullable=True)