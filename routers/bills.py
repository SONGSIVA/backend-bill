from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List
from datetime import datetime
from database import get_db
import models, schemas

router = APIRouter(prefix="/bills", tags=["Bills"])


def generate_invoice_number(db: Session) -> str:
    now = datetime.now()
    prefix = f"INV-{now.strftime('%Y%m')}-"
    count = db.query(models.Bill).filter(
        models.Bill.invoice_number.like(f"{prefix}%")
    ).count()
    return f"{prefix}{str(count + 1).zfill(4)}"


@router.get("/", response_model=List[schemas.BillResponse])
def get_all_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Bill).options(
        joinedload(models.Bill.customer),
        joinedload(models.Bill.items)
    ).order_by(models.Bill.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.BillResponse, status_code=201)
def create_bill(bill_data: schemas.BillCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == bill_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    subtotal = 0.0
    bill_items_data = []
    for bill_item in bill_data.items:
        item = db.query(models.Item).filter(models.Item.id == bill_item.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {bill_item.item_id} not found")
        total_price = round(bill_item.quantity * bill_item.unit_price, 2)
        subtotal += total_price
        bill_items_data.append({
            "item_id": bill_item.item_id,
            "quantity": bill_item.quantity,
            "unit_price": bill_item.unit_price,
            "total_price": total_price,
        })

    cgst_amount = round(subtotal * bill_data.cgst_rate / 100, 2)
    sgst_amount = round(subtotal * bill_data.sgst_rate / 100, 2)
    total_amount = round(subtotal + cgst_amount + sgst_amount, 2)

    db_bill = models.Bill(
        invoice_number=generate_invoice_number(db),
        customer_id=bill_data.customer_id,
        subtotal=round(subtotal, 2),
        cgst_rate=bill_data.cgst_rate,
        sgst_rate=bill_data.sgst_rate,
        cgst_amount=cgst_amount,
        sgst_amount=sgst_amount,
        total_amount=total_amount,
        notes=bill_data.notes,
    )
    db.add(db_bill)
    db.flush()

    for bi in bill_items_data:
        db_bill_item = models.BillItem(bill_id=db_bill.id, **bi)
        db.add(db_bill_item)

    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/{bill_id}", response_model=schemas.BillResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).options(
        joinedload(models.Bill.customer),
        joinedload(models.Bill.items)
    ).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.put("/{bill_id}", response_model=schemas.BillResponse)
def update_bill(bill_id: int, bill_data: schemas.BillCreate, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    customer = db.query(models.Customer).filter(models.Customer.id == bill_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Delete existing items
    db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).delete()

    subtotal = 0.0
    bill_items_data = []
    for bill_item in bill_data.items:
        item = db.query(models.Item).filter(models.Item.id == bill_item.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {bill_item.item_id} not found")
        total_price = round(bill_item.quantity * bill_item.unit_price, 2)
        subtotal += total_price
        bill_items_data.append({
            "item_id": bill_item.item_id,
            "quantity": bill_item.quantity,
            "unit_price": bill_item.unit_price,
            "total_price": total_price,
        })

    cgst_amount = round(subtotal * bill_data.cgst_rate / 100, 2)
    sgst_amount = round(subtotal * bill_data.sgst_rate / 100, 2)
    total_amount = round(subtotal + cgst_amount + sgst_amount, 2)

    bill.customer_id = bill_data.customer_id
    bill.subtotal = round(subtotal, 2)
    bill.cgst_rate = bill_data.cgst_rate
    bill.sgst_rate = bill_data.sgst_rate
    bill.cgst_amount = cgst_amount
    bill.sgst_amount = sgst_amount
    bill.total_amount = total_amount
    bill.notes = bill_data.notes

    for bi in bill_items_data:
        db.add(models.BillItem(bill_id=bill_id, **bi))

    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", status_code=204)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill)
    db.commit()
