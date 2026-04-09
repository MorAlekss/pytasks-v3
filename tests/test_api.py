import sys
sys.path.insert(0, '.')
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

async def _test_get_user_async():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('src.api.users.httpx.AsyncClient', return_value=mock_client):
        from src.api.users import get_user
        result = await get_user(1)
        assert result["id"] == 1

async def _test_get_product_async():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Widget"}
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('src.api.products.httpx.AsyncClient', return_value=mock_client):
        from src.api.products import get_product
        result = await get_product(1)
        assert result["name"] == "Widget"

def test_get_user():
    asyncio.run(_test_get_user_async())

def test_get_product():
    asyncio.run(_test_get_product_async())

if __name__ == "__main__":
    test_get_user()
    test_get_product()
    print("all tests passed")
