from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.orders import Order, OrderItem
from backend.app.models.inventory import Product, StockBatch, StockMove
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import selectinload

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class CreateOrderRequest(BaseModel):
    user_id: int
    customer_id: Optional[int] = None
    items: List[OrderItemCreate]
    is_takeout: bool = False
    notes: Optional[str] = None
    status: str = "paid"

router = APIRouter()

@router.post("/orders/", response_model=Order)
def create_order(
    request: CreateOrderRequest,
    session: Session = Depends(get_session)
):
    """
    Creates an order and deducts stock using First-Expiry-First-Out (FEFO) logic.
    """
    total_amount = 0.0

    # 1. Create Order
    order = Order(
        user_id=request.user_id,
        customer_id=request.customer_id,
        is_takeout=request.is_takeout,
        notes=request.notes,
        status=request.status,
        created_at=datetime.utcnow()
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    # 2. Process Items
    for item_data in request.items:
        prod_id = item_data.product_id
        qty_needed = item_data.quantity

        product = session.get(Product, prod_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {prod_id} not found")

        if product.stock_quantity < qty_needed:
             raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}. Have: {product.stock_quantity}, Need: {qty_needed}")

        unit_price = product.price
        total_amount += (unit_price * qty_needed)

        # --- FEFO LOGIC ---
        batches = session.exec(
            select(StockBatch)
            .where(StockBatch.product_id == prod_id, StockBatch.quantity > 0)
            .order_by(StockBatch.expiry_date.asc())
        ).all()

        remaining_qty = qty_needed

        for batch in batches:
            if remaining_qty <= 0:
                break

            deduct = min(batch.quantity, remaining_qty)
            batch.quantity -= deduct
            remaining_qty -= deduct
            session.add(batch)

        # Update product total stock
        product.stock_quantity -= qty_needed
        session.add(product)

        # --- STOCK MOVE (LEDGER) ---
        move = StockMove(
            product_id=prod_id,
            quantity=-qty_needed, # Negative for sale
            move_type="sale",
            reference=f"Order #{order.id}"
        )
        session.add(move)

        # Create Order Item
        order_item = OrderItem(
            order_id=order.id,
            product_id=prod_id,
            quantity=qty_needed,
            unit_price=unit_price
        )
        session.add(order_item)

    order.total_amount = total_amount
    session.add(order)
    session.commit()
    session.refresh(order)

    # Return order with items eagerly loaded
    refreshed_order = session.exec(
        select(Order).where(Order.id == order.id).options(selectinload(Order.items))
    ).first()

    return refreshed_order

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
    order = session.exec(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
