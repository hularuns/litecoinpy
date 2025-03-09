import aiohttp
import asyncio
from typing import List, Dict, Any
from src.exceptions import LitePyConnectionError
from src.utils import get_logger
import time

GLOBAL_TIME_LIMIT = 5

class LitePy:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.base_url = "https://litecoinspace.org/api/"
        
    async def get_address(self, ltc_address: str) -> Dict[str, Any] | None:
        """
        Returns details about a Litecoin address.
        
        Args:
            ltc_address (str): The Litecoin address to lookup
            
        Returns:
            Dict[str, Any]: Address details containing fields:
            - address: The Litecoin address
            - chain_stats: Object with tx_count, funded_txo_count, funded_txo_sum,
                       spent_txo_count, and spent_txo_sum
            - mempool_stats: Object with the same fields as chain_stats
        """
        built_url = f"{self.base_url}address/{ltc_address}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(built_url, allow_redirects = True, timeout = 10) as response:
                    if response.status != 200:
                        self.logger.error(f"Error getting address: {response.status}")
                        raise LitePyConnectionError("Error getting address")
                    return await response.json()
        except aiohttp.ClientError as e:
            raise LitePyConnectionError("Error getting address") from e
            
if __name__ == "__main__":
    ltc = LitePy()
    ltc_address = "LbPQBNUPSDJvoD6aw7pSEiSs6R2VjMVeNX"
    print(asyncio.run(ltc.get_address(ltc_address)))