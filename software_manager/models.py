from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Software(Base):
    __tablename__ = "software"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    version = Column(String, default=True)
    status = Column(String, default=True)

class ApiKey(Base):
    __tablename__ = "api_key"

    key = Column(String, primary_key=True, index=True)
    activated = Column(Boolean, default=True)