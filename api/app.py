from fastapi import FastAPI
import csv

app = FastAPI()


@app.get("/inventory")
def get_inventory():
    with open("products.csv", "r", encoding = "utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)