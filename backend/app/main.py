from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.database import create_db_and_tables
from backend.app.api import inventory, orders

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Local ERP AI", version="0.1", lifespan=lifespan)

app.include_router(inventory.router, prefix="/api/v1", tags=["inventory"])
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Local ERP AI Backend"}
