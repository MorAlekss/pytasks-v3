import sys
sys.path.insert(0, '.')
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


def test_get_user():
    async def run_test():
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch('src.api.users.httpx.AsyncClient', return_value=mock_client):
            from src.api.users import get_user
            result = await get_user(1)
            assert result["id"] == 1

    asyncio.run(run_test())


def test_get_product():
    async def run_test():
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Widget"}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch('src.api.products.httpx.AsyncClient', return_value=mock_client):
            from src.api.products import get_product
            result = await get_product(1)
            assert result["name"] == "Widget"

    asyncio.run(run_test())


test_get_user()
test_get_product()
print("all tests passed")
