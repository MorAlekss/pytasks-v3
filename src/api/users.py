import httpx

BASE_URL = "https://api.example.com"

async def get_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    return response.json()

async def create_user(data):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/users", json=data)
    response.raise_for_status()
    return response.json()

async def update_user(user_id, data):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{BASE_URL}/users/{user_id}", json=data)
    response.raise_for_status()
    return response.json()

async def delete_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    return response.status_code
