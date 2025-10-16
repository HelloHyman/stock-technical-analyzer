"""
Caching utilities for the Stock Analysis Application
"""

import threading
import time
from typing import Any, Dict, Optional


class DataCache:
    """
    Thread-safe cache for storing data with TTL (Time To Live) support.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize the cache.
        
        Args:
            ttl_seconds: Time to live for cached items in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def get(self, symbol: str, period: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        key = f"{symbol.upper()}_{period}"
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if time.time() - entry['timestamp'] > self._ttl:
                del self._cache[key]
                return None
            
            return entry['value']

    def set(self, symbol: str, period: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            symbol: Stock symbol
            period: Time period
            value: Value to cache
        """
        key = f"{symbol.upper()}_{period}"
        with self._lock:
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get the number of cached items."""
        with self._lock:
            return len(self._cache)
