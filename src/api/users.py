import requests

BASE_URL = "https://api.example.com"

def get_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    return response.json()

def create_user(data):
    response = requests.post(f"{BASE_URL}/users", json=data)
    response.raise_for_status()
    return response.json()

def update_user(user_id, data):
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=data)
    response.raise_for_status()
    return response.json()

def delete_user(user_id):
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    return response.status_code
