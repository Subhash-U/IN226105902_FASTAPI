from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

cart = []
orders = []
order_id_counter = 1


@app.get("/")
def home():
    return {"message": "Product API running"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.post("/products", status_code=201)
def add_product(name: str, price: int, category: str, in_stock: bool):
    for p in products:
        if p["name"].lower() == name.lower():
            raise HTTPException(status_code=400, detail="Product with this name already exists")

    new_product = {
        "id": len(products) + 1,
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    category: Optional[str] = None,
    in_stock: Optional[bool] = None
):
    for product in products:
        if product["id"] == product_id:

            if name is not None:
                product["name"] = name
            if price is not None:
                product["price"] = price
            if category is not None:
                product["category"] = category
            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return {"message": f"Product '{product['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")


@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):
    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    grand_total = sum(item["subtotal"] for item in cart)

    orders_placed = []

    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"],
            "delivery_address": delivery_address
        }

        orders.append(order)
        orders_placed.append(order)
        order_id_counter += 1

    cart.clear()

    return {
        "orders_placed": len(orders_placed),
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }