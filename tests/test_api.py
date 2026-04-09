import sys
sys.path.insert(0, '.')
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_get_user():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch('httpx.AsyncClient', return_value=mock_client):
        from src.api.users import get_user
        result = await get_user(1)
        assert result["id"] == 1

@pytest.mark.asyncio
async def test_get_product():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Widget"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch('httpx.AsyncClient', return_value=mock_client):
        from src.api.products import get_product
        result = await get_product(1)
        assert result["name"] == "Widget"

if __name__ == "__main__":
    asyncio.run(test_get_user())
    asyncio.run(test_get_product())
    print("all tests passed")
