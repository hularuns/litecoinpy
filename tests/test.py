import pytest

from src.litecoinpy import litecoinpy
from unittest.mock import patch, AsyncMock
import aiohttp

@pytest.mark.asyncio
async def test_get_address():
    ltc = litecoinpy()
    ltc_address = "LbPQBNUPSDJvoD6aw7pSEiSs6R2VjMVeNX"
    response = await ltc.get_address(ltc_address)   
    assert response, "Response is empty"
    assert isinstance(response, dict), "Response is not a dictionary as expected"
    assert response["address"] == ltc_address, "Response address does not match input address"
