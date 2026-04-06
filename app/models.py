from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False, unique=True)
    environment = Column(String, nullable=False, default="lab")
    owner = Column(String, nullable=False, default="security-team")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    results = relationship("ScanResult", back_populates="asset", cascade="all, delete-orphan")


class ScanResult(Base):
    __tablename__ = "scan_results"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    scan_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    asset = relationship("Asset", back_populates="results")
