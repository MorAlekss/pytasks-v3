import sys
sys.path.insert(0, '.')
import httpx
from unittest.mock import patch, MagicMock
import pytest

@pytest.mark.asyncio
async def test_get_user():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        from src.api.users import aget_user
        result = await aget_user(1)
        assert result["id"] == 1

@pytest.mark.asyncio
async def test_get_product():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Widget"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        from src.api.products import aget_product
        result = await aget_product(1)
        assert result["name"] == "Widget"
