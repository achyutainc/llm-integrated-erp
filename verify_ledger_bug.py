import requests
import sys

def verify_stock_ledger():
    BASE_URL = "http://localhost:8000/api/v1"

    # 1. Create a Product
    print("Creating product...")
    cat_res = requests.post(f"{BASE_URL}/categories/", json={"name": "Test Cat"})
    cat_id = cat_res.json()["id"]

    prod_res = requests.post(f"{BASE_URL}/products/", json={
        "name": "Audit Item", "price": 10.0, "stock_quantity": 0, "category_id": cat_id
    })
    prod_id = prod_res.json()["id"]

    # 2. Simulate Manual Adjustment (IN)
    print("Adjusting stock IN...")
    requests.post(f"{BASE_URL}/inventory/adjust", json={
        "product_id": prod_id, "quantity_change": 20, "reason": "Initial Count"
    })

    # 3. Simulate Sale (OUT)
    print("Creating Order...")
    order_data = {
        "user_id": 1,
        "items": [{"product_id": prod_id, "quantity": 5}]
    }
    requests.post(f"{BASE_URL}/orders/", json=order_data)

    # 4. Check Ledger
    print("Checking Ledger...")
    moves_res = requests.get(f"{BASE_URL}/inventory/moves?product_id={prod_id}")
    moves = moves_res.json()

    # Expect 3 moves:
    # 1. "Manual Batch Add" from add_stock_batch (Wait, adjust endpoint creates separate move? No, logic check needed)
    # The 'adjust' endpoint creates a move.
    # FEFO logic in 'adjust' endpoint handles batch deduction if negative.
    # But wait, my test used `inventory/adjust` which adds +20.

    # Let's check api implementation of `adjust_inventory`:
    # It adds product.stock_quantity += change.
    # It creates a StockMove.
    # Does it create a Batch if positive?
    # Looking at `adjust_inventory` code: It updates `product.stock_quantity`. It DOES NOT create a `StockBatch` if positive!
    # This is a flaw in my implementation. Positive adjustment needs to land in a batch or it effectively "floats" without expiry.
    # However, for this verification script, I just want to see the ledger.

    # For order creation, it requires batches to deduct from (FEFO).
    # Since `adjust_inventory` didn't create a batch, `create_order` might fail if `product.stock_quantity` is high but `batches` are empty!

    # CRITICAL FINDING: `adjust_inventory` +positive must create a batch.
    # `create_order` relies on `StockBatch` existence.

    pass

if __name__ == "__main__":
    # Just running logic check mentally, I found a bug.
    pass
