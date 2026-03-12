from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


@app.get("/")
def home():
    return {"message": "Product API running"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="discount_percent must be between 1 and 99")

    updated_products = []

    for product in products:
        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated_products.append({
                "name": product["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }



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

    return {
        "message": "Product added",
        "product": new_product
    }


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


@app.get("/products/audit")
def audit_products():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }




@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")