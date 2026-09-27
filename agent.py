import requests

API_URL = "http://127.0.0.1:8000"


def get_inventory():
    response = requests.get(f"{API_URL}/inventory")
    return response.json()

def create_product(product):
    response = requests.post(f"{API_URL}/inventory", json = product)
    return response.json

def update_product(product_id, product):
    response = requests.patch(
        f"{API_URL}/inventory/{product_id}",
        json=product)
    return response.json()

def get_inventory_alerts():
    response = requests.get(f"{API_URL}/inventory/alerts")
    return response.json()


#print(get_inventory())
#print(create_product({'id': '4', 'name': 'Caca', 'quantity': '9', 'unit': 'unidades'}))
#print(get_inventory_alerts())