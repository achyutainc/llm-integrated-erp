from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.app.database import get_session
from backend.app.models.customer import Customer

router = APIRouter()

@router.post("/customers/", response_model=Customer)
def create_customer(customer: Customer, session: Session = Depends(get_session)):
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@router.get("/customers/", response_model=List[Customer])
def read_customers(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    search: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Customer)
    if search:
        # Search by name or phone
        query = query.where((Customer.name.contains(search)) | (Customer.phone.contains(search)))

    customers = session.exec(query.offset(offset).limit(limit)).all()
    return customers

@router.get("/customers/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, session: Session = Depends(get_session)):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
