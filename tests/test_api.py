import sys
import asyncio
sys.path.insert(0, '.')
from unittest.mock import patch, MagicMock, AsyncMock

def test_get_user():
    with patch('src.api.users.httpx.AsyncClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)
        from src.api.users import get_user
        result = asyncio.run(get_user(1))
        assert result["id"] == 1

def test_get_product():
    with patch('src.api.products.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Widget"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        from src.api.products import get_product
        result = get_product(1)
        assert result["name"] == "Widget"

test_get_user()
test_get_product()
print("all tests passed")
