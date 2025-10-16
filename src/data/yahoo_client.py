"""
Yahoo Finance API client with rate limiting and caching
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import yfinance as yf

from ..config.constants import YAHOO_MAX_RPS
from ..config.dependencies import retry, retry_if_exception_type, wait_exponential, stop_after_attempt, RETRY_AVAILABLE, TENACITY_AVAILABLE
from ..utils.rate_limiter import TokenBucket


@dataclass
class YahooClient:
    """
    Yahoo Finance API client with built-in rate limiting and caching.
    """

    ticker_symbol: str
    _ticker: yf.Ticker = field(init=False)
    _cache: Dict[str, Any] = field(default_factory=dict, init=False)
    _limiter: TokenBucket = field(default_factory=lambda: TokenBucket(YAHOO_MAX_RPS), init=False)

    def __post_init__(self) -> None:
        """Initialize the Yahoo Finance ticker."""
        # IMPORTANT: do NOT pass a requests/session into yf.Ticker now
        self._ticker = yf.Ticker(self.ticker_symbol)

    def _throttled(self, fn_name: str, call) -> Any:
        """
        Execute a function with throttling and caching.
        
        Args:
            fn_name: Function name for caching
            call: Function to execute
            
        Returns:
            Function result
        """
        if fn_name in self._cache:
            return self._cache[fn_name]
        
        # throttle before any yfinance call (since we can't inject a session)
        self._limiter.acquire()
        
        val = call()
        self._cache[fn_name] = val
        return val

    def _retryable(self, func, *args, **kwargs):
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        if RETRY_AVAILABLE and TENACITY_AVAILABLE:
            @retry(
                retry=retry_if_exception_type(Exception),
                wait=wait_exponential(multiplier=0.8, min=1, max=20),
                stop=stop_after_attempt(6),
                reraise=True,
            )
            def _retry_wrapper():
                return func(*args, **kwargs)
            
            return _retry_wrapper()
        else:
            # Fallback to direct execution if retry libraries not available
            return func(*args, **kwargs)

    def history(self, period: str = "2y", interval: str = "1d") -> Any:
        """
        Get historical data.
        
        Args:
            period: Data period
            interval: Data interval
            
        Returns:
            Historical data
        """
        key = f"history:{period}:{interval}"
        return self._throttled(key, lambda: self._retryable(self._ticker.history, period=period, interval=interval))

    def info(self) -> Dict[str, Any]:
        """
        Get ticker info.
        
        Returns:
            Ticker information
        """
        return self._throttled("info", lambda: dict(self._ticker.info or {}))

    def options(self) -> List[str]:
        """
        Get available options expiration dates.
        
        Returns:
            List of expiration date strings
        """
        return self._throttled("options", lambda: list(self._ticker.options or []))

    def option_chain(self, expiration: str) -> Any:
        """
        Get options chain for a specific expiration.
        
        Args:
            expiration: Expiration date string
            
        Returns:
            Options chain data
        """
        key = f"option_chain:{expiration}"
        return self._throttled(key, lambda: self._retryable(self._ticker.option_chain, expiration))
