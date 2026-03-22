from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()


products = [
    {"id": 1, "name": "Casual Shirt", "brand": "Zara", "category": "Shirt", "price": 1500, "sizes_available": ["S","M","L"], "in_stock": True},
    {"id": 2, "name": "Denim Jeans", "brand": "Levis", "category": "Jeans", "price": 2500, "sizes_available": ["M","L"], "in_stock": True},
    {"id": 3, "name": "Running Shoes", "brand": "Nike", "category": "Shoes", "price": 4000, "sizes_available": ["8","9","10"], "in_stock": False},
    {"id": 4, "name": "Summer Dress", "brand": "H&M", "category": "Dress", "price": 1800, "sizes_available": ["S","M"], "in_stock": True},
    {"id": 5, "name": "Leather Jacket", "brand": "Zara", "category": "Jacket", "price": 5000, "sizes_available": ["M","L"], "in_stock": True},
    {"id": 6, "name": "Sneakers", "brand": "Adidas", "category": "Shoes", "price": 3500, "sizes_available": ["7","8","9"], "in_stock": True},
]

orders = []
wishlist = []
order_counter = 1

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=10)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False


class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    sizes_available: List[str]
    in_stock: bool = True


def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def calculate_order_total(price, quantity, gift_wrap, season_sale):
    base = price * quantity

    season_discount = base * 0.15 if season_sale else 0
    bulk_discount = base * 0.05 if quantity >= 5 else 0

    total_discount = season_discount + bulk_discount
    gift_cost = 50 * quantity if gift_wrap else 0

    final_total = base - total_discount + gift_cost

    return {
        "base_price": base,
        "season_discount": season_discount,
        "bulk_discount": bulk_discount,
        "total_discount": total_discount,
        "gift_wrap_cost": gift_cost,
        "final_total": final_total
    }




@app.get("/")
def home():
    return {"message": "Welcome to TrendZone Fashion Store"}


@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products),
        "in_stock_count": sum(1 for p in products if p["in_stock"])
    }


@app.get("/products/summary")
def summary():
    brands = list(set(p["brand"] for p in products))

    category_count = {}
    for p in products:
        category_count[p["category"]] = category_count.get(p["category"], 0) + 1

    return {
        "total": len(products),
        "in_stock": sum(1 for p in products if p["in_stock"]),
        "out_of_stock": sum(1 for p in products if not p["in_stock"]),
        "brands": brands,
        "category_count": category_count
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders),
        "total_revenue": sum(o["total"] for o in orders)
    }



@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    max_price: Optional[int] = None,
    in_stock: Optional[bool] = None
):
    result = products

    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if brand is not None:
        result = [p for p in result if p["brand"].lower() == brand.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"results": result, "count": len(result)}



@app.get("/products/search")
def search_products(keyword: str):
    result = [
        p for p in products
        if keyword.lower() in p["name"].lower()
        or keyword.lower() in p["brand"].lower()
        or keyword.lower() in p["category"].lower()
    ]

    if not result:
        return {"message": "No products found"}

    return {"results": result, "total_found": len(result)}


@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    valid = ["price", "name", "brand", "category"]

    if sort_by not in valid:
        raise HTTPException(400, "Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    reverse = True if order == "desc" else False

    sorted_data = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "data": sorted_data}


@app.get("/products/page")
def paginate_products(page: int = Query(1, gt=0), limit: int = Query(3, gt=0)):
    total = len(products)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": products[start:end]
    }


@app.get("/products/browse")
def browse(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    max_price: Optional[int] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = products

    # keyword filter
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
            or keyword.lower() in p["brand"].lower()
            or keyword.lower() in p["category"].lower()
        ]

    # other filters
    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if brand is not None:
        result = [p for p in result if p["brand"].lower() == brand.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    # sorting
    if sort_by not in ["price", "name", "brand", "category"]:
        raise HTTPException(400, "Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    # pagination
    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "data": result[start:end]
    }


@app.post("/products", status_code=201)
def add_product(product: NewProduct):
    for p in products:
        if p["name"] == product.name and p["brand"] == product.brand:
            raise HTTPException(400, "Product already exists")

    new = product.dict()
    new["id"] = len(products) + 1
    products.append(new)
    return new


@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):
    product = find_product(product_id)

    if not product:
        raise HTTPException(404, "Not found")

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = find_product(product_id)

    if not product:
        raise HTTPException(404, "Not found")

    for o in orders:
        if o["product_id"] == product_id:
            raise HTTPException(400, "Cannot delete product with orders")

    products.remove(product)
    return {"message": "Deleted"}


@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    global order_counter

    product = find_product(order.product_id)

    if not product:
        raise HTTPException(404, "Product not found")

    if not product["in_stock"]:
        raise HTTPException(400, "Product out of stock")

    if order.size not in product["sizes_available"]:
        raise HTTPException(400, f"Available sizes: {product['sizes_available']}")

    calc = calculate_order_total(
        product["price"],
        order.quantity,
        order.gift_wrap,
        order.season_sale
    )

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product_id": product["id"],
        "product_name": product["name"],
        "brand": product["brand"],
        "size": order.size,
        "quantity": order.quantity,
        "delivery_address": order.delivery_address,
        "price_breakdown": calc,
        "total": calc["final_total"]
    }

    orders.append(new_order)
    order_counter += 1

    return new_order


@app.post("/wishlist/add")
def add_wishlist(customer_name: str, product_id: int, size: str):
    product = find_product(product_id)

    if not product:
        raise HTTPException(404, "Product not found")

    if size not in product["sizes_available"]:
        raise HTTPException(400, "Invalid size")

    for item in wishlist:
        if item["customer_name"] == customer_name and item["product_id"] == product_id and item["size"] == size:
            raise HTTPException(400, "Already in wishlist")

    wishlist.append({
        "customer_name": customer_name,
        "product_id": product_id,
        "size": size
    })

    return {"message": "Added to wishlist"}


@app.get("/wishlist")
def get_wishlist():
    total_value = 0

    for item in wishlist:
        product = find_product(item["product_id"])
        if product:
            total_value += product["price"]

    return {"wishlist": wishlist, "total_value": total_value}


@app.delete("/wishlist/remove")
def remove_wishlist(customer_name: str, product_id: int):
    for item in wishlist:
        if item["customer_name"] == customer_name and item["product_id"] == product_id:
            wishlist.remove(item)
            return {"message": "Removed"}

    raise HTTPException(404, "Not found")


@app.post("/wishlist/order-all", status_code=201)
def order_all(data: dict):
    global order_counter

    customer = data.get("customer_name")
    address = data.get("delivery_address")

    user_items = [w for w in wishlist if w["customer_name"] == customer]

    if not user_items:
        raise HTTPException(400, "No wishlist items")

    created_orders = []
    total_cost = 0

    for item in user_items:
        product = find_product(item["product_id"])

        calc = calculate_order_total(product["price"], 1, False, False)

        order = {
            "order_id": order_counter,
            "customer_name": customer,
            "product_id": product["id"],
            "product_name": product["name"],
            "brand": product["brand"],
            "size": item["size"],
            "quantity": 1,
            "delivery_address": address,
            "total": calc["final_total"]
        }

        orders.append(order)
        created_orders.append(order)
        total_cost += calc["final_total"]

        order_counter += 1

    for item in user_items:
        wishlist.remove(item)

    return {"orders": created_orders, "grand_total": total_cost}


@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"results": result}


@app.get("/orders/sort")
def sort_orders(sort_by: str = "total"):
    valid = ["total", "quantity"]

    if sort_by not in valid:
        raise HTTPException(400, "Invalid sort field")

    return {"data": sorted(orders, key=lambda x: x[sort_by])}


@app.get("/orders/page")
def page_orders(page: int = Query(1, gt=0), limit: int = Query(2, gt=0)):
    total = len(orders)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": orders[start:end]
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)

    if not product:
        raise HTTPException(404, "Product not found")

    return product