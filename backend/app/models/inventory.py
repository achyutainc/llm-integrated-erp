from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date, datetime

class StockBatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=0)
    # Changed to str to avoid SQLite/Pydantic date parsing issues in test environment.
    # ISO Format YYYY-MM-DD strings sort and compare correctly.
    expiry_date: Optional[str] = None
    received_date: date = Field(default_factory=date.today)

    product: "Product" = Relationship(back_populates="batches")

# Circular import prevention: Define Product here or import if split
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    stock_quantity: int = Field(default=0) # Aggregate of batches (for quick lookup)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(back_populates="products")
    is_takeout: bool = Field(default=False)

    # New Fields for POS
    barcode: Optional[str] = Field(default=None, index=True, unique=True)
    image_url: Optional[str] = None

    batches: List[StockBatch] = Relationship(back_populates="product")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # New Fields for POS
    image_url: Optional[str] = None

    products: List[Product] = Relationship(back_populates="category")
