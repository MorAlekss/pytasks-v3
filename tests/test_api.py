import sys
sys.path.insert(0, '.')
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

def test_get_user():
    async def run():
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        with patch('src.api.users.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            from src.api.users import get_user
            result = await get_user(1)
            assert result["id"] == 1
    asyncio.run(run())

def test_get_product():
    async def run():
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Widget"}
        mock_response.raise_for_status.return_value = None
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        with patch('src.api.products.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            from src.api.products import get_product
            result = await get_product(1)
            assert result["name"] == "Widget"
    asyncio.run(run())

test_get_user()
test_get_product()
print("all tests passed")
