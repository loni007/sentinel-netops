from pathlib import Path
import asyncio
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Asset, ScanResult
from .schemas import AssetCreate, AssetOut, ScanResultOut
from .scanner import health_check, safe_port_scan
from .security import require_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Sentinel NetOps", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.get("/api/assets", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).order_by(Asset.id.desc()).all()


@app.post("/api/assets", response_model=AssetOut)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), _: None = Depends(require_token)):
    existing = db.query(Asset).filter(Asset.host == payload.host).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset host already exists")
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@app.get("/api/results", response_model=list[ScanResultOut])
def list_results(db: Session = Depends(get_db)):
    return db.query(ScanResult).order_by(ScanResult.id.desc()).limit(100).all()


@app.post("/api/assets/{asset_id}/health-check", response_model=ScanResultOut)
def run_health_check(asset_id: int, db: Session = Depends(get_db), _: None = Depends(require_token)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    result = asyncio.run(health_check(asset.host))
    row = ScanResult(asset_id=asset.id, scan_type="health_check", status=result["status"], details=result["details"])
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/api/assets/{asset_id}/port-scan", response_model=ScanResultOut)
def run_port_scan(asset_id: int, db: Session = Depends(get_db), _: None = Depends(require_token)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    result = asyncio.run(safe_port_scan(asset.host))
    row = ScanResult(asset_id=asset.id, scan_type="safe_port_scan", status=result["status"], details=result["details"])
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
