"""
Rate limiting utilities for API calls
"""

import time
import threading
from typing import Optional


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    """

    def __init__(self, rate: float, capacity: Optional[int] = None):
        """
        Initialize the token bucket.
        
        Args:
            rate: Tokens per second
            capacity: Maximum number of tokens (defaults to rate * 2)
        """
        self.rate = rate
        self.capacity = capacity or int(rate * 2)
        self.tokens = self.capacity
        self.last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False if bucket is empty
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False

    def wait_for_tokens(self, tokens: int = 1) -> None:
        """
        Wait until tokens are available.
        
        Args:
            tokens: Number of tokens to wait for
        """
        while not self.acquire(tokens):
            time.sleep(0.01)  # Small delay to avoid busy waiting
