from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from backend.app.models.inventory import Product

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float # Snapshot of price at purchase time

    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship()

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int # Assume external auth or simple staff ID for now
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="draft") # draft, paid, delivered, pickup
    total_amount: float = Field(default=0.0)
    is_takeout: bool = Field(default=False) # Ecommerce vs Takeout Restaurant logic

    items: List[OrderItem] = Relationship(back_populates="order")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    role: str = Field(default="staff") # admin, manager, staff, driver
    hashed_password: str
