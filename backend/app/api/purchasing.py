from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.purchasing import Vendor, PurchaseOrder, PurchaseOrderItem, SupplierPricelist
from backend.app.models.inventory import Product, StockBatch
from datetime import date

router = APIRouter()

# --- VENDORS ---

@router.post("/vendors/", response_model=Vendor)
def create_vendor(vendor: Vendor, session: Session = Depends(get_session)):
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

@router.get("/vendors/", response_model=List[Vendor])
def read_vendors(session: Session = Depends(get_session)):
    return session.exec(select(Vendor)).all()

# --- PURCHASE ORDERS ---

@router.post("/purchase-orders/", response_model=PurchaseOrder)
def create_po(po: PurchaseOrder, session: Session = Depends(get_session)):
    session.add(po)
    session.commit()
    session.refresh(po)
    return po

@router.get("/purchase-orders/", response_model=List[PurchaseOrder])
def read_pos(session: Session = Depends(get_session)):
    return session.exec(select(PurchaseOrder)).all()

@router.post("/purchase-orders/{po_id}/items/", response_model=PurchaseOrderItem)
def add_po_item(
    po_id: int,
    item: PurchaseOrderItem,
    session: Session = Depends(get_session)
):
    po = session.get(PurchaseOrder, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    item.purchase_order_id = po_id
    session.add(item)

    # Update PO Total (Simplified)
    po.total_amount += (item.unit_cost * item.quantity)
    session.add(po)

    session.commit()
    session.refresh(item)
    return item

@router.post("/purchase-orders/{po_id}/receive")
def receive_po(po_id: int, session: Session = Depends(get_session)):
    """
    Mark PO as received and add to StockBatches.
    """
    po = session.get(PurchaseOrder, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    if po.status == "received":
        raise HTTPException(status_code=400, detail="PO already received")

    # Process items into stock
    for item in po.items:
        # Create a stock batch
        # We assume 30 days expiry by default if not specified, or user manually updates later
        # For MVP, we just set it to None or calculated if we had lead time info
        batch = StockBatch(
            product_id=item.product_id,
            quantity=item.quantity,
            received_date=date.today()
        )
        session.add(batch)

        # Update product total stock
        product = session.get(Product, item.product_id)
        if product:
            product.stock_quantity += item.quantity
            session.add(product)

    po.status = "received"
    session.add(po)
    session.commit()
    return {"message": "Purchase Order received and inventory updated"}
