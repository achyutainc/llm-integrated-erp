from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, pool
from backend.app.main import app
from backend.app.database import get_session
import pytest
from datetime import date, datetime

# Use an in-memory SQLite database for testing
sqlite_file_name = "database.db"
# Use in-memory database
sqlite_url = "sqlite://"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, poolclass=pool.StaticPool)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Local ERP AI Backend"}

def test_create_category():
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Grocery"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Grocery"
    assert data["id"] is not None

def test_create_product():
    # first create a category
    cat_response = client.post("/api/v1/categories/", json={"name": "Takeout"})
    cat_id = cat_response.json()["id"]

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Milk",
            "price": 3.99,
            "stock_quantity": 50,
            "category_id": cat_id,
            "barcode": "123456789"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Milk"
    assert data["price"] == 3.99
    assert data["stock_quantity"] == 50

def test_read_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_order_with_fefo():
    # 1. Create Product & Stock Batches
    cat_res = client.post("/api/v1/categories/", json={"name": "Grocery"})
    cat_id = cat_res.json()["id"]

    prod_res = client.post("/api/v1/products/", json={
        "name": "Old Milk", "price": 10.0, "stock_quantity": 0, "category_id": cat_id
    })
    prod_id = prod_res.json()["id"]

    # Batch 1: Expires soon (2 days)
    # The error "SQLite Date type only accepts Python date objects as input" implies the test/SQLAlchemy
    # is receiving a string for a Date column.
    # When using TestClient, we send JSON (strings).
    # FastAPI/Pydantic converts JSON string -> Python date object in the route handler.
    # The route handler adds the object to the session.
    # The issue might be specific to how SQLModel/Pydantic v2 handles date parsing in this specific environment.

    # Let's verify the route handler is getting a date object.
    # But first, let's try creating the batch using the API normally.

    res1 = client.post(f"/api/v1/products/{prod_id}/batches/", json={
        "product_id": prod_id, "quantity": 10, "expiry_date": "2026-03-01"
    })

    # If this fails, the issue is in the batch creation API logic/model.
    if res1.status_code != 200:
        print("Batch creation failed:", res1.json())
    assert res1.status_code == 200

    # Batch 2: Expires later (10 days)
    client.post(f"/api/v1/products/{prod_id}/batches/", json={
        "product_id": prod_id, "quantity": 10, "expiry_date": "2026-03-10"
    })

    # 2. Create Order for 15 units
    order_data = {
        "user_id": 1,
        "items": [
            {"product_id": prod_id, "quantity": 15}
        ]
    }

    response = client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["total_amount"] == 150.0

    # 3. Verify Stock Deduction (FEFO)
    # Batch 1 should be empty (10 used)
    # Batch 2 should have 5 left (5 used)
    alerts_res = client.get("/api/v1/inventory/alerts?days=30")
    batches = alerts_res.json()

    # Filter for this product
    my_batches = [b for b in batches if b["product_id"] == prod_id]

    # Sort by expiry to be safe
    my_batches.sort(key=lambda x: x["expiry_date"])

    # Batch 1 (Expires March 1) -> Should be 0, but the alert endpoint filters out 0 qty batches!
    # So we should only see Batch 2 with 5 units.
    assert len(my_batches) == 1
    assert my_batches[0]["quantity"] == 5
    assert my_batches[0]["expiry_date"] == "2026-03-10"
