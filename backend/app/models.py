from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    stock_quantity: int = Field(default=0)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="products")
    is_takeout: bool = Field(default=False)

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
    status: str = Field(default="draft") # draft, paid, delivered
    total_amount: float = Field(default=0.0)

    items: List[OrderItem] = Relationship(back_populates="order")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    role: str = Field(default="staff") # admin, manager, staff, driver
    hashed_password: str
