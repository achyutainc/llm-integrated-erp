from sqlmodel import SQLModel, create_engine, Session
import os

# Use SQLite by default, but allow override for Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grocery.db")

# check_same_thread is needed for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
