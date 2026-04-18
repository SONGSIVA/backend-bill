from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
import models

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_DIR = BASE_DIR / "static" / "logos"
LOGO_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/settings", tags=["Settings"])


class CompanySettingsSchema(BaseModel):
    company_name: str
    gst_no: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/company", response_model=CompanySettingsSchema)
def get_company_settings(request: Request, db: Session = Depends(get_db)):
    settings = db.query(models.CompanySettings).first()
    if not settings:
        return CompanySettingsSchema(company_name="My Company")

    if settings.logo_url and settings.logo_url.startswith("/logos/"):
        filename = settings.logo_url.split("/logos/", 1)[1]
        settings.logo_url = str(request.url_for("logos", path=filename))
    return settings


@router.post("/company/logo")
def upload_company_logo(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/svg+xml", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported logo file type.")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported logo file extension.")

    filename = f"logo_{uuid4().hex}{ext}"
    destination = LOGO_DIR / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    settings = db.query(models.CompanySettings).first()
    if not settings:
        settings = models.CompanySettings(company_name="My Company")
        db.add(settings)

    settings.logo_url = f"/logos/{filename}"
    db.commit()
    db.refresh(settings)

    full_logo_url = request.url_for("logos", path=filename)
    return {"logo_url": settings.logo_url, "full_logo_url": str(full_logo_url)}


@router.post("/company", response_model=CompanySettingsSchema)
def save_company_settings(data: CompanySettingsSchema, db: Session = Depends(get_db)):
    payload = data.model_dump(exclude_unset=True)
    settings = db.query(models.CompanySettings).first()
    if settings:
        for field, value in payload.items():
            setattr(settings, field, value)
    else:
        settings = models.CompanySettings(**payload)
        db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
