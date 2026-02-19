from sqlmodel import Session, select
from backend.app.database import engine, create_db_and_tables
from backend.app.models.inventory import Product, Category, StockBatch
from backend.app.models.marketing import SocialMediaPost
from backend.app.models.orders import User
from datetime import date, timedelta

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

        # Products (Ontario Grocery & Takeout - Expanded)
        products_data = [
            {"name": "Milk (2L)", "price": 5.49, "stock": 50, "cat": grocery, "desc": "2% Milk, Ontario Dairy", "expiry": date.today() + timedelta(days=5)}, # Expiring soon
            {"name": "Bread (Whole Wheat)", "price": 3.99, "stock": 30, "cat": grocery, "desc": "Local bakery whole wheat bread", "expiry": date.today() + timedelta(days=3)}, # Expiring very soon
            {"name": "Butter Chicken", "price": 14.99, "stock": 20, "cat": takeout, "desc": "Creamy tomato curry with chicken", "is_takeout": True},
            {"name": "Naan Bread", "price": 2.50, "stock": 100, "cat": takeout, "desc": "Garlic Naan", "is_takeout": True},
            {"name": "Apples (Honeycrisp)", "price": 0.99, "stock": 200, "cat": grocery, "desc": "Ontario Honeycrisp Apples per lb", "expiry": date.today() + timedelta(days=14)},
            {"name": "Basmati Rice (10lb)", "price": 18.99, "stock": 40, "cat": grocery, "desc": "Premium Long Grain Basmati Rice"},
            {"name": "Shan Biryani Masala", "price": 1.99, "stock": 100, "cat": grocery, "desc": "Spice mix for Biryani"},
        ]

        for p_data in products_data:
            p = Product(
                name=p_data["name"],
                price=p_data["price"],
                stock_quantity=p_data["stock"],
                category_id=p_data["cat"].id,
                description=p_data.get("desc"),
                is_takeout=p_data.get("is_takeout", False)
            )
            session.add(p)
            session.commit()
            session.refresh(p)

            # Create a batch if expiry provided
            if "expiry" in p_data:
                batch = StockBatch(
                    product_id=p.id,
                    quantity=p_data["stock"],
                    expiry_date=p_data["expiry"]
                )
                session.add(batch)

        # Marketing Posts
        posts = [
            SocialMediaPost(platform="facebook", content="Fresh Ontario Apples arrived! Come get your Honeycrisp today. #SupportLocal", status="draft"),
            SocialMediaPost(platform="instagram", content="Craving Butter Chicken? Order now for pickup! 🍛 #Takeout #IndianFood", status="scheduled", scheduled_date=date.today() + timedelta(days=1))
        ]
        for post in posts:
            session.add(post)

        # Admin User
        admin = User(username="admin", hashed_password="hashed_password_placeholder", role="admin")
        session.add(admin)

        session.commit()
        print("Seeded database successfully with inventory and marketing data.")

if __name__ == "__main__":
    seed()
