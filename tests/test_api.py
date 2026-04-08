import sys
sys.path.insert(0, '.')
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_get_user():
    with patch('src.api.users.httpx.AsyncClient') as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        from src.api.users import get_user
        result = await get_user(1)
        assert result["id"] == 1

@pytest.mark.asyncio
async def test_get_product():
    with patch('src.api.products.httpx.AsyncClient') as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Widget"}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        from src.api.products import get_product
        result = await get_product(1)
        assert result["name"] == "Widget"
