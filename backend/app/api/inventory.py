from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.inventory import Product, Category, StockBatch, StockMove
from datetime import date, timedelta
from pydantic import BaseModel

router = APIRouter()

class AdjustmentRequest(BaseModel):
    product_id: int
    quantity_change: int # Negative to reduce stock
    reason: str

@router.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.get("/products/", response_model=List[Product])
def read_products(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products

@router.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/categories/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/categories/", response_model=List[Category])
def read_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories

@router.post("/products/{product_id}/batches/", response_model=StockBatch)
def add_stock_batch(
    product_id: int,
    batch: StockBatch,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    batch.product_id = product_id
    session.add(batch)

    # Update total stock
    product.stock_quantity += batch.quantity
    session.add(product)

    # Create Ledger Entry
    move = StockMove(
        product_id=product_id,
        quantity=batch.quantity,
        move_type="adjustment_in",
        reference="Manual Batch Add"
    )
    session.add(move)

    session.commit()
    session.refresh(batch)
    return batch

@router.get("/inventory/alerts", response_model=List[StockBatch])
def get_expiry_alerts(
    days: int = 7,
    session: Session = Depends(get_session)
):
    threshold_date = (date.today() + timedelta(days=days)).isoformat()
    statement = select(StockBatch).where(
        StockBatch.expiry_date != None,
        StockBatch.expiry_date <= threshold_date,
        StockBatch.quantity > 0
    )
    batches = session.exec(statement).all()
    return batches

@router.post("/inventory/adjust", response_model=StockMove)
def adjust_inventory(
    req: AdjustmentRequest,
    session: Session = Depends(get_session)
):
    """
    Manually adjust inventory (e.g., spoilage, theft, correction).
    """
    product = session.get(Product, req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validation
    if req.quantity_change < 0 and product.stock_quantity < abs(req.quantity_change):
        raise HTTPException(status_code=400, detail="Cannot reduce stock below zero.")

    # Update Product Total
    product.stock_quantity += req.quantity_change
    session.add(product)

    # Handle Batches
    if req.quantity_change > 0:
        batch = StockBatch(
            product_id=req.product_id,
            quantity=req.quantity_change,
            # No expiry set for adjustment unless we expand API.
        )
        session.add(batch)

    elif req.quantity_change < 0:
        qty_to_remove = abs(req.quantity_change)
        batches = session.exec(
            select(StockBatch)
            .where(StockBatch.product_id == req.product_id, StockBatch.quantity > 0)
            .order_by(StockBatch.expiry_date.asc())
        ).all()

        for batch in batches:
            if qty_to_remove <= 0:
                break
            deduct = min(batch.quantity, qty_to_remove)
            batch.quantity -= deduct
            qty_to_remove -= deduct
            session.add(batch)

    # Record Ledger Move
    move = StockMove(
        product_id=req.product_id,
        quantity=req.quantity_change,
        move_type="adjustment",
        reference=req.reason
    )
    session.add(move)
    session.commit()
    session.refresh(move)
    return move

@router.get("/inventory/moves", response_model=List[StockMove])
def get_stock_moves(
    product_id: Optional[int] = None,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    query = select(StockMove).order_by(StockMove.date.desc()).limit(limit)
    if product_id:
        query = query.where(StockMove.product_id == product_id)
    return session.exec(query).all()
