from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, pool
from backend.app.main import app
from backend.app.database import get_session
import pytest

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
    # Clear tables after test?
    # With in-memory static pool, it might persist across tests if we don't drop.
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
            "category_id": cat_id
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

def test_create_order():
    response = client.post(
        "/api/v1/orders/",
        json={"user_id": 1, "total_amount": 10.50}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["status"] == "draft"
