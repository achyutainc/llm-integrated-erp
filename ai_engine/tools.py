import requests
import json
import os
from typing import List, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/v1")

# --- EXISTING TOOLS ---

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


# --- NEW TOOLS FOR STAFF & CUSTOMER AGENTS ---

def check_expiry_alert(days: int = 7) -> str:
    """
    Checks for products expiring within the given number of days.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/inventory/alerts?days={days}")
        response.raise_for_status()
        batches = response.json()

        if not batches:
            return "✅ No items expiring soon."

        # For simplicity, we assume we fetch product names manually if backend doesn't hydrate batch.product
        # In reality, the backend response might include nested product info if we enabled response_model=ReadWithProduct
        # Let's assume we fetch products to get names or just check product_id if lazy.

        # Since we are lazy and want to avoid another round trip for names if not needed:
        # Let's just list the IDs or assume we can query product names efficiently.
        # Actually, let's fetch product list once and map IDs.

        products_res = requests.get(f"{BACKEND_URL}/products/")
        all_products = products_res.json()
        prod_map = {p['id']: p['name'] for p in all_products}

        alert_msg = "⚠️ Expiring Soon:\n"
        for b in batches:
            p_name = prod_map.get(b['product_id'], f"Product #{b['product_id']}")
            alert_msg += f"- {p_name}: {b['quantity']} units (Expires {b['expiry_date']})\n"

        return alert_msg
    except Exception as e:
        return f"Error checking expiry: {str(e)}"

def generate_marketing_draft(platform: str, topic: str) -> str:
    """
    Generates a draft social media post.
    """
    try:
        content = f"Draft for {topic}: Come visit us for the best {topic} in town! #{platform} #Local"

        # We need to ensure the backend accepts this.
        # The backend expects: platform, content, status
        post_data = {
            "platform": platform,
            "content": content,
            "status": "draft"
        }
        res = requests.post(f"{BACKEND_URL}/posts/", json=post_data)
        res.raise_for_status()
        return f"Draft post created for {platform}: '{content}'"
    except Exception as e:
        return f"Error creating post: {str(e)}"

def suggest_recipe_products(dish_name: str) -> str:
    """
    Suggests products for a given dish.
    """
    dish_lower = dish_name.lower()

    recipes = {
        "butter chicken": ["Chicken", "Butter Chicken", "Naan Bread", "Basmati Rice"],
        "biryani": ["Basmati Rice", "Shan Biryani Masala", "Chicken", "Yogurt"],
        "curry": ["Curry Powder", "Chicken", "Vegetables", "Rice"],
    }

    ingredients = []
    found_recipe = False
    for key, items in recipes.items():
        if key in dish_lower:
            ingredients = items
            found_recipe = True
            break

    if not found_recipe:
        # Fallback if no specific recipe found in hardcoded list
        # In real AI, the LLM handles this logic, this tool is just a lookup
        return f"I don't have a verified recipe for {dish_name} in my database, but you can search for ingredients!"

    # Search for these items in stock
    found = []
    # Mock search for known ingredients to ensure tool works
    # In reality, search_products would be called
    try:
        all_prods_res = requests.get(f"{BACKEND_URL}/products/")
        if all_prods_res.ok:
            all_prods = all_prods_res.json()
            # Basic fuzzy match
            all_names = [p['name'].lower() for p in all_prods]

            for ing in ingredients:
                ing_lower = ing.lower()
                matched = False
                for name in all_names:
                    if ing_lower in name:
                        matched = True
                        break
                if matched:
                    found.append(ing)
    except:
        return "Error connecting to inventory."

    if found:
        return f"To make {dish_name}, we have these ingredients in stock: {', '.join(found)}!"
    else:
        return f"We seem to be out of specific ingredients for {dish_name}."
