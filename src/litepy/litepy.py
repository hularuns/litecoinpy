import aiohttp
import asyncio
from typing import List, Dict, Any
from src.exceptions import LitePyConnectionError, LitePyInvalidRateLimit
from src.utils import get_logger
import time

class LitePy:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.base_url = "https://litecoinspace.org/api/"
        self.last_request_time = 0
        self.request_interval = 6 #seconds
        self.rate_limit_multiplier = 2
        self.error_threshold = 8 # Retries a max of 8 times...
        self.current_retry = 0

    def _throttle(func):
        """Decorator to ensure API requests are throttled"""
        async def wrapper(self, *args, **kwargs):
            now = time.time()
            elapsed = now - self.last_request_time

            if elapsed < self.request_interval:
                delay = self.request_interval - elapsed
                self.logger.debug(f"Throttling request for {delay:.2f}s")
                await asyncio.sleep(delay)

            self.last_request_time = time.time()
            return await func(self, *args, **kwargs)
        return wrapper

    @_throttle
    async def get_address(
        self,
        ltc_address: str,
        throttle_seconds: int = 6
    ) -> Dict[str, Any] | None:
        """
        Returns details about a Litecoin address.
        
        Args:
            ltc_address (str): The Litecoin address to lookup
            throttle_seconds (int): Number of seconds to throttle requests to prevent rate limiting
            
        Returns:
            Dict[str, Any]: Address details containing fields:
            - address: The Litecoin address
            - chain_stats: Object with tx_count, funded_txo_count, funded_txo_sum,
                       spent_txo_count, and spent_txo_sum
            - mempool_stats: Object with the same fields as chain_stats
        """
        # Update the request interval if a new value is provided
        self.request_interval = throttle_seconds
        
        built_url = f"{self.base_url}address/{ltc_address}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(built_url, allow_redirects = True, timeout = 10) as response:
                    if response.status == 429:
                        self.logger.error(f"Rate limited by server: {response.status}")
                        self.request_interval *= self.rate_limit_multiplier
                        if self.current_retry < self.error_threshold:
                            self.current_retry += 1
                            self.logger.debug(f"Retrying request {self.current_retry} of {self.error_threshold}")
                            return await self.get_address(ltc_address, self.request_interval)
                        else:
                            self.logger.error(f"Max retries reached: {self.current_retry}")
                            raise LitePyInvalidRateLimit("Max retries reached")
                    
                    if response.status != 200:
                        self.logger.error(f"Error getting address: {response.status}")
                        raise LitePyConnectionError("Error getting address")
                    return await response.json()
                
        except aiohttp.ClientError as e:
            raise LitePyConnectionError("Error getting address")


if __name__ == "__main__":
    ltc = LitePy()
    ltc_address = "qwdqd"
    for i in range(2):
        print(asyncio.run(ltc.get_address(ltc_address)))
