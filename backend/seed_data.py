from sqlmodel import Session, select
from backend.app.database import engine, create_db_and_tables
from backend.app.models.inventory import Product, Category, StockBatch
from backend.app.models.marketing import SocialMediaPost
from backend.app.models.orders import User
from backend.app.models.customer import Customer
from backend.app.models.purchasing import Vendor
from datetime import date, timedelta

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if data exists
        if session.exec(select(Product)).first():
            print("Data already seeded.")
            return

        # Categories
        grocery = Category(name="Grocery", image_url="https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=200&q=80")
        takeout = Category(name="Takeout", image_url="https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=200&q=80")
        session.add(grocery)
        session.add(takeout)
        session.commit()
        session.refresh(grocery)
        session.refresh(takeout)

        # Products (Ontario Grocery & Takeout - Expanded)
        products_data = [
            {"name": "Milk (2L)", "price": 5.49, "stock": 50, "cat": grocery, "desc": "2% Milk, Ontario Dairy", "expiry": date.today() + timedelta(days=5), "barcode": "000123456789", "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=200&q=80"},
            {"name": "Bread (Whole Wheat)", "price": 3.99, "stock": 30, "cat": grocery, "desc": "Local bakery whole wheat bread", "expiry": date.today() + timedelta(days=3), "barcode": "000987654321", "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=200&q=80"},
            {"name": "Butter Chicken", "price": 14.99, "stock": 20, "cat": takeout, "desc": "Creamy tomato curry with chicken", "is_takeout": True, "img": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=200&q=80"},
            {"name": "Naan Bread", "price": 2.50, "stock": 100, "cat": takeout, "desc": "Garlic Naan", "is_takeout": True, "img": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=200&q=80"},
            {"name": "Apples (Honeycrisp)", "price": 0.99, "stock": 200, "cat": grocery, "desc": "Ontario Honeycrisp Apples per lb", "expiry": date.today() + timedelta(days=14), "barcode": "333333333333", "img": "https://images.unsplash.com/photo-1567306301408-9b74779a11af?auto=format&fit=crop&w=200&q=80"},
            {"name": "Basmati Rice (10lb)", "price": 18.99, "stock": 40, "cat": grocery, "desc": "Premium Long Grain Basmati Rice", "barcode": "111111111111", "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=200&q=80"},
            {"name": "Shan Biryani Masala", "price": 1.99, "stock": 100, "cat": grocery, "desc": "Spice mix for Biryani", "barcode": "222222222222", "img": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=200&q=80"},
        ]

        for p_data in products_data:
            p = Product(
                name=p_data["name"],
                price=p_data["price"],
                stock_quantity=p_data["stock"],
                category_id=p_data["cat"].id,
                description=p_data.get("desc"),
                is_takeout=p_data.get("is_takeout", False),
                barcode=p_data.get("barcode"),
                image_url=p_data.get("img")
            )
            session.add(p)
            session.commit()
            session.refresh(p)

            # Create a batch if expiry provided
            if "expiry" in p_data:
                # Convert date to string for SQLite compatibility in StockBatch
                batch = StockBatch(
                    product_id=p.id,
                    quantity=p_data["stock"],
                    expiry_date=p_data["expiry"].isoformat()
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

        # Sample Customers
        customers = [
            Customer(name="John Doe", phone="555-123-4567", email="john@example.com", points=100),
            Customer(name="Jane Smith", phone="555-987-6543", email="jane@example.com", points=50),
        ]
        for c in customers:
            session.add(c)

        # Sample Vendors
        vendors = [
            Vendor(name="Ontario Dairy Coop", code="V-001", contact_name="Bob Farmer", email="bob@dairy.ca", payment_terms="Net 15"),
            Vendor(name="Global Spices Imports", code="V-002", contact_name="Raj Patel", email="raj@spices.com", payment_terms="Net 30"),
            Vendor(name="Costco Business Center", code="V-003", contact_name="Manager", payment_terms="Due on Receipt")
        ]
        for v in vendors:
            session.add(v)

        session.commit()
        print("Seeded database successfully with inventory, marketing, customers, and vendors.")

if __name__ == "__main__":
    seed()
