from pydantic import BaseModel, Field
from typing import Optional


class AssetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    environment: str = "lab"
    owner: str = "security-team"


class AssetOut(BaseModel):
    id: int
    name: str
    host: str
    environment: str
    owner: str
    is_active: bool

    class Config:
        from_attributes = True


class ScanResultOut(BaseModel):
    id: int
    asset_id: int
    scan_type: str
    status: str
    details: str

    class Config:
        from_attributes = True
