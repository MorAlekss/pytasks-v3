import httpx

BASE_URL = "https://api.example.com"

async def get_product(product_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()

async def list_products(category=None):
    params = {"category": category} if category else {}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products", params=params)
        response.raise_for_status()
        return response.json()

async def create_product(data):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/products", json=data)
        response.raise_for_status()
        return response.json()
