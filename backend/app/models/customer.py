from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: str = Field(index=True, unique=True)
    email: Optional[str] = None
    points: int = Field(default=0)
    notes: Optional[str] = None
