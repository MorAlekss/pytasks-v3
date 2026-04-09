import sys
sys.path.insert(0, '.')
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

def test_get_user():
    with patch('src.api.users.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        from src.api.users import get_user
        result = get_user(1)
        assert result["id"] == 1

def test_get_product():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Widget"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False

    with patch('src.api.products.httpx.AsyncClient', return_value=mock_client):
        from src.api.products import get_product
        result = asyncio.run(get_product(1))
        assert result["name"] == "Widget"

test_get_user()
test_get_product()
print("all tests passed")
