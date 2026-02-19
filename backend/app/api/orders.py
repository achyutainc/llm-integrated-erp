from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models import Order, OrderItem, Product

router = APIRouter()

@router.post("/orders/", response_model=Order)
def create_order(order: Order, session: Session = Depends(get_session)):
    # Calculate total and validate stock if needed (omitted for brevity in MVP)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@router.get("/orders/", response_model=List[Order])
def read_orders(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders

@router.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders/{order_id}/items/", response_model=OrderItem)
def create_order_item(
    order_id: int,
    item: OrderItem,
    session: Session = Depends(get_session)
):
    # Verify Order exists
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify Product exists
    product = session.get(Product, item.product_id)
    if not product:
         raise HTTPException(status_code=404, detail="Product not found")

    item.order_id = order_id
    # Could update order total here
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
