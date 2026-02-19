import requests
import json
from typing import List, Optional

BACKEND_URL = "http://localhost:8000/api/v1"

def search_products(query: str) -> str:
    """
    Searches for products in the inventory.
    Currently fetches all products and filters client-side (MVP).
    """
    try:
        response = requests.get(f"{BACKEND_URL}/products/")
        response.raise_for_status()
        products = response.json()

        # Simple fuzzy search
        results = [
            p for p in products
            if query.lower() in p["name"].lower() or
               (p["description"] and query.lower() in p["description"].lower())
        ]

        if not results:
            return "No products found matching that description."

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error connecting to inventory system: {str(e)}"

def check_stock(product_name: str) -> str:
    """
    Checks the stock level of a specific product.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/products/")
        response.raise_for_status()
        products = response.json()

        for p in products:
            if p["name"].lower() == product_name.lower():
                return f"Product: {p['name']}, Stock: {p['stock_quantity']}, Price: ${p['price']}"

        return f"Product '{product_name}' not found."
    except Exception as e:
        return f"Error checking stock: {str(e)}"

def create_order_tool(user_id: int, product_names: List[str]) -> str:
    """
    Creates a draft order for a list of product names.
    """
    try:
        # 1. Create Order
        order_res = requests.post(f"{BACKEND_URL}/orders/", json={"user_id": user_id})
        order_res.raise_for_status()
        order = order_res.json()
        order_id = order["id"]

        # 2. Find Products and add to order
        # Fetch all products once for lookup
        prod_res = requests.get(f"{BACKEND_URL}/products/")
        prod_res.raise_for_status()
        all_products = prod_res.json()

        added_items = []
        missing_items = []

        for name in product_names:
            product = next((p for p in all_products if p["name"].lower() == name.lower()), None)
            if product:
                item_data = {
                    "product_id": product["id"],
                    "quantity": 1,
                    "unit_price": product["price"]
                }
                requests.post(f"{BACKEND_URL}/orders/{order_id}/items/", json=item_data)
                added_items.append(name)
            else:
                missing_items.append(name)

        result = f"Order #{order_id} created with: {', '.join(added_items)}."
        if missing_items:
            result += f" Could not find: {', '.join(missing_items)}."

        return result
    except Exception as e:
        return f"Error creating order: {str(e)}"

def agent_create_order(product_names_comma_separated: str) -> str:
    """
    Useful for creating a new order. Input should be a comma-separated list of product names (e.g. "milk, bread").
    """
    names = [n.strip() for n in product_names_comma_separated.split(",")]
    # Hardcode user_id=1 for the agent context for now
    return create_order_tool(user_id=1, product_names=names)
