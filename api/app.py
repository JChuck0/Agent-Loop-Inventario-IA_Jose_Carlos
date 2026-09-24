from fastapi import FastAPI
import csv
from pydantic import BaseModel

class Product(BaseModel):
    name :str
    quantity : int
    unit : str

app = FastAPI()


@app.get("/inventory")
def get_inventory():
    with open("products.csv", "r", encoding = "utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)

@app.post("/inventory")
def create_product(product: Product):

    # 1. Leer los productos que ya existen
    with open("products.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        products = list(reader)

    # 2. Generar el siguiente ID
    if products:
        new_id = max(int(p["id"]) for p in products) + 1
    else:
        new_id = 1

    # 3. Construir el nuevo producto
    new_product = {
        "id": new_id,
        "name": product.name,
        "quantity": product.quantity,
        "unit": product.unit
    }

    # 4. Añadirlo al CSV
    with open("products.csv", "a", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "name", "quantity", "unit"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(new_product)

    # 5. Devolver el producto creado
    return new_product


@app.patch("/inventory/{product_id}")
def update_product_quantity(product_id: int, quantity: int):

    # 1. Leer todos los productos
    with open("products.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        products = list(reader)

    # 2. Buscar el producto y actualizar su cantidad
    product_found = None

    for product in products:
        if int(product["id"]) == product_id:
            product["quantity"] = str(quantity)
            product_found = product
            break

    # 3. Si no existe el producto, devolver error
    if product_found is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # 4. Reescribir el CSV con los datos actualizados
    with open("products.csv", "w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "name", "quantity", "unit"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(products)

    # 5. Devolver el producto actualizado
    return product_found