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
def post_inventory(product : Product):
    with open("poducts.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, filenames = ["id", "name", "quantity", "unit"])
    pass


