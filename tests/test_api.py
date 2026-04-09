import sys
sys.path.insert(0, '.')
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_get_user():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch('src.api.users.httpx.AsyncClient') as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        from src.api.users import get_user
        result = await get_user(1)
        assert result["id"] == 1

@pytest.mark.asyncio
async def test_get_product():
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Widget"}
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch('src.api.products.httpx.AsyncClient') as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        from src.api.products import get_product
        result = await get_product(1)
        assert result["name"] == "Widget"
