from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date

# Circular import solution: Use string forward references for relationships if needed
# But simple models are fine.

class Vendor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True) # e.g. "V-001"
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_terms: str = Field(default="Net 30") # Net 30, COD, etc.

    pricelists: List["SupplierPricelist"] = Relationship(back_populates="vendor")
    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="vendor")

class SupplierPricelist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: int = Field(foreign_key="vendor.id")
    product_id: int = Field(foreign_key="product.id")
    cost: float
    min_order_qty: int = Field(default=1)
    lead_time_days: int = Field(default=7)
    vendor_product_code: Optional[str] = None

    vendor: Vendor = Relationship(back_populates="pricelists")
    # Link to Inventory Product
    # We need to import Product, but avoid circular import if Product imports this.
    # Usually Product doesn't need to know about pricelists directly unless we add a relationship there.

class PurchaseOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: int = Field(foreign_key="vendor.id")
    status: str = Field(default="draft") # draft, sent, received, cancelled
    order_date: date = Field(default_factory=date.today)
    expected_date: Optional[date] = None
    total_amount: float = Field(default=0.0)
    notes: Optional[str] = None

    vendor: Vendor = Relationship(back_populates="purchase_orders")
    items: List["PurchaseOrderItem"] = Relationship(back_populates="purchase_order")

class PurchaseOrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_order_id: int = Field(foreign_key="purchaseorder.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_cost: float

    purchase_order: PurchaseOrder = Relationship(back_populates="items")
