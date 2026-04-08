import requests

BASE_URL = "https://api.example.com"

def get_product(product_id):
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    response.raise_for_status()
    return response.json()

def list_products(category=None):
    params = {"category": category} if category else {}
    response = requests.get(f"{BASE_URL}/products", params=params)
    response.raise_for_status()
    return response.json()

def create_product(data):
    response = requests.post(f"{BASE_URL}/products", json=data)
    response.raise_for_status()
    return response.json()
