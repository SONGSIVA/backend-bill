from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
import models

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

    class Config:
        from_attributes = True


@router.get("/company", response_model=CompanySettingsSchema)
def get_company_settings(db: Session = Depends(get_db)):
    settings = db.query(models.CompanySettings).first()
    if not settings:
        return CompanySettingsSchema(company_name="My Company")
    return settings


@router.post("/company", response_model=CompanySettingsSchema)
def save_company_settings(data: CompanySettingsSchema, db: Session = Depends(get_db)):
    settings = db.query(models.CompanySettings).first()
    if settings:
        for field, value in data.model_dump().items():
            setattr(settings, field, value)
    else:
        settings = models.CompanySettings(**data.model_dump())
        db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
