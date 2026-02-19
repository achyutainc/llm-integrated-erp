from sqlmodel import Session, select
from backend.app.database import engine, create_db_and_tables
from backend.app.models import Product, Category, User

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if data exists
        if session.exec(select(Product)).first():
            print("Data already seeded.")
            return

        # Categories
        grocery = Category(name="Grocery")
        takeout = Category(name="Takeout")
        session.add(grocery)
        session.add(takeout)
        session.commit()
        session.refresh(grocery)
        session.refresh(takeout)

        # Products (Ontario Grocery & Takeout)
        products = [
            Product(name="Milk (2L)", price=5.49, stock_quantity=50, category_id=grocery.id, description="2% Milk, Ontario Dairy"),
            Product(name="Bread (Whole Wheat)", price=3.99, stock_quantity=30, category_id=grocery.id, description="Local bakery whole wheat bread"),
            Product(name="Butter Chicken", price=14.99, stock_quantity=20, category_id=takeout.id, is_takeout=True, description="Creamy tomato curry with chicken"),
            Product(name="Naan Bread", price=2.50, stock_quantity=100, category_id=takeout.id, is_takeout=True, description="Garlic Naan"),
            Product(name="Apples (Honeycrisp)", price=0.99, stock_quantity=200, category_id=grocery.id, description="Ontario Honeycrisp Apples per lb"),
            Product(name="Maple Syrup (500ml)", price=12.99, stock_quantity=40, category_id=grocery.id, description="Pure Ontario Maple Syrup"),
        ]

        for p in products:
            session.add(p)

        # Admin User
        admin = User(username="admin", hashed_password="hashed_password_placeholder", role="admin")
        session.add(admin)

        session.commit()
        print("Seeded database successfully.")

if __name__ == "__main__":
    seed()
