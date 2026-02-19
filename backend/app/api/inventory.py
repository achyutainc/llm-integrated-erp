from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.inventory import Product, Category, StockBatch
from datetime import date, timedelta

router = APIRouter()

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

    session.commit()
    session.refresh(batch)
    return batch

@router.get("/inventory/alerts", response_model=List[StockBatch])
def get_expiry_alerts(
    days: int = 7,
    session: Session = Depends(get_session)
):
    """
    Returns stock batches expiring within the specified number of days.
    """
    threshold_date = date.today() + timedelta(days=days)
    # Query for batches expiring soon (assuming expiry_date is set)
    statement = select(StockBatch).where(
        StockBatch.expiry_date != None,
        StockBatch.expiry_date <= threshold_date,
        StockBatch.quantity > 0 # Only list if we actually have stock
    )
    batches = session.exec(statement).all()
    return batches
