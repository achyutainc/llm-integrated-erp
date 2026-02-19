import requests
import time

def verify_stock_ledger():
    BASE_URL = "http://localhost:8000/api/v1"

    # 1. Create a Product
    print("Creating product...")
    cat_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Audit Cat"})
    if not cat_res.ok: return
    cat_id = cat_res.json()["id"]

    prod_res = requests.post(f"{BASE_URL}/products/", json={
        "name": "Audit Item", "price": 10.0, "stock_quantity": 0, "category_id": cat_id
    })
    prod_id = prod_res.json()["id"]

    # 2. Simulate Manual Adjustment (IN) - Should create batch
    print("Adjusting stock IN (+20)...")
    adj_res = requests.post(f"{BASE_URL}/inventory/adjust", json={
        "product_id": prod_id, "quantity_change": 20, "reason": "Initial Count"
    })
    if not adj_res.ok:
        print("Adjustment failed:", adj_res.text)
        return

    # 3. Simulate Sale (OUT) - Should deduct from batch created above
    print("Creating Order (-5)...")
    order_data = {
        "user_id": 1,
        "items": [{"product_id": prod_id, "quantity": 5}]
    }
    order_res = requests.post(f"{BASE_URL}/orders/", json=order_data)
    if not order_res.ok:
        print("Order failed:", order_res.text)
        return

    # 4. Check Ledger
    print("Checking Ledger...")
    moves_res = requests.get(f"{BASE_URL}/inventory/moves?product_id={prod_id}")
    moves = moves_res.json()

    print(f"Found {len(moves)} moves.")
    for m in moves:
        print(f" - {m['move_type']}: {m['quantity']} (Ref: {m['reference']})")

    if len(moves) >= 2:
        print("SUCCESS: Ledger recorded adjustment and sale.")
    else:
        print("FAILURE: Missing ledger entries.")

if __name__ == "__main__":
    verify_stock_ledger()
