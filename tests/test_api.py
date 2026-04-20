import sys
import asyncio
sys.path.insert(0, '.')
from unittest.mock import patch, MagicMock, AsyncMock

def test_get_user():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch('src.api.users.httpx.AsyncClient', return_value=mock_client):
        from src.api.users import get_user
        result = asyncio.get_event_loop().run_until_complete(get_user(1))
        assert result["id"] == 1

def test_get_product():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Widget"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch('src.api.products.httpx.AsyncClient', return_value=mock_client):
        from src.api.products import get_product
        result = asyncio.get_event_loop().run_until_complete(get_product(1))
        assert result["name"] == "Widget"

test_get_user()
test_get_product()
print("all tests passed")
