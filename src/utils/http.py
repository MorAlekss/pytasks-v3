import requests

def get_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def post_json(url, data):
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()
