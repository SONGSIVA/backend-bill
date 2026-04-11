from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


# ── Item Schemas ──────────────────────────────────────────────
class ItemBase(BaseModel):
    item_code: str
    item_name: str
    unit_price: float
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    unit_price: Optional[float] = None
    description: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Customer Schemas ──────────────────────────────────────────
class CustomerBase(BaseModel):
    customer_id: str
    customer_name: str
    mobile: str
    address: Optional[str] = None
    gst_no: Optional[str] = None
    postal_code: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    gst_no: Optional[str] = None
    postal_code: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bill Schemas ──────────────────────────────────────────────
class BillItemCreate(BaseModel):
    item_id: int
    quantity: float
    unit_price: float


class BillItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: float
    unit_price: float
    total_price: float
    item: ItemResponse

    class Config:
        from_attributes = True


class BillCreate(BaseModel):
    customer_id: int
    cgst_rate: float = 9.0
    sgst_rate: float = 9.0
    items: List[BillItemCreate]
    notes: Optional[str] = None


class BillResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    subtotal: float
    cgst_rate: float
    sgst_rate: float
    cgst_amount: float
    sgst_amount: float
    total_amount: float
    notes: Optional[str]
    created_at: datetime
    customer: CustomerResponse
    items: List[BillItemResponse]

    class Config:
        from_attributes = True
