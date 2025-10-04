#!/usr/bin/env python3
"""
Comprehensive Stock and Crypto Analyzer - Technical + Fundamental Analysis
- Enter any stock/crypto symbol for complete analysis
- Interactive chart with moving averages and technical indicators
- Support/Resistance levels and RSI analysis
- 5-Pillar Fundamental Analysis (Profitability, Growth, Balance Sheet, Market Position, Forward Outlook)
- Social sentiment analysis from StockTwits
- Options chain evaluation
- Earnings calendar integration
- Customizable timeframes and chart settings
- Optimized for fast startup and performance
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime

# Core data libraries
import pandas as pd
import numpy as np

# Try to import heavy libraries with fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    print("Warning: yfinance not available. Please install with: pip install yfinance")
    YFINANCE_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.lines import Line2D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not available. Please install with: pip install matplotlib")
    MATPLOTLIB_AVAILABLE = False

try:
    import mplfinance as mpf
    MPLFINANCE_AVAILABLE = True
except ImportError:
    print("Warning: mplfinance not available. Please install with: pip install mplfinance")
    MPLFINANCE_AVAILABLE = False

try:
    import requests
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from requests_cache import CachedSession
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests/tenacity/requests_cache not available. Social sentiment analysis will be disabled.")
    REQUESTS_AVAILABLE = False

# -----------------------------------------------------------------------------
# FUNDAMENTAL ANALYSIS CONFIGURATION
# -----------------------------------------------------------------------------

# Rate Limiting Configuration
YAHOO_MAX_RPS = 1.2          # Be conservative; yfinance now uses curl_cffi internally
STOCKTWITS_MAX_RPS = 1.0     # StockTwits stricter
HTTP_CACHE_TTL = 60          # seconds for HTTP GET cache
REQUEST_TIMEOUT = 12         # seconds

# Fundamental Scoring Thresholds
MIN_PROFIT_MARGIN = 0.10        # 10%
MIN_OPER_MARGIN = 0.10          # 10%
MIN_QTR_REV_GROWTH = 0.05       # 5% QoQ revenue growth
MIN_POSITIVE_QTRS = 60.0        # 60% of last 5y quarters positive
MIN_REV_TO_DEBT = 2.0           # Revenue / Total Debt
MIN_OCF_TO_DEBT = 0.50          # OCF must be >= 50% of Total Debt
MAX_DECLINE_FROM_HIGH = 0.30    # within 30% of 52w high
REQUIRED_PASS_COUNT = 4         # need 4/5 pillars to PASS

# -----------------------------------------------------------------------------
# DATA CACHING AND PERFORMANCE
# -----------------------------------------------------------------------------

class DataCache:
    """Simple cache for stock data to improve performance."""
    
    def __init__(self, max_size: int = 32, ttl_seconds: int = 300):
        self.cache: Dict[str, Tuple[pd.DataFrame, float]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cached data is expired."""
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get cached data if available and not expired."""
        key = f"{symbol.upper()}_{period}"
        if key in self.cache:
            data, timestamp = self.cache[key]
            if not self._is_expired(timestamp):
                return data.copy()
            else:
                del self.cache[key]
        return None
    
    def set(self, symbol: str, period: str, data: pd.DataFrame) -> None:
        """Cache the data."""
        key = f"{symbol.upper()}_{period}"
        
        # Simple LRU: remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (data.copy(), time.time())

# Global cache instance
_data_cache = DataCache()

# -----------------------------------------------------------------------------
# RATE LIMITING AND HTTP CLIENT
# -----------------------------------------------------------------------------

class TokenBucket:
    """
    Simple token-bucket limiter for per-host throttling.
    capacity tokens refill at 'rate' (tokens per second).
    """
    def __init__(self, rate: float, capacity: Optional[float] = None) -> None:
        self.rate = float(rate)
        self.capacity = float(capacity) if capacity is not None else float(rate)
        self.tokens = self.capacity
        self.timestamp = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            # Refill tokens based on elapsed time
            elapsed = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            # If no tokens, wait
            if self.tokens < 1.0:
                need = 1.0 - self.tokens
                sleep_for = need / self.rate
                time.sleep(max(0.0, sleep_for))
                # after sleeping, consume immediately
                self.timestamp = time.monotonic()
                self.tokens = max(0.0, self.tokens + sleep_for * self.rate)
            # Consume 1 token
            self.tokens -= 1.0

class HttpClient:
    def __init__(self) -> None:
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests/tenacity/requests_cache required for HTTP client")
        
        # Cached session for REST GETs (StockTwits only)
        self.session = CachedSession(
            cache_name="http_cache",
            backend="memory",
            expire_after=HTTP_CACHE_TTL,
            allowable_methods=("GET",),
        )
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })
        self._limiter = TokenBucket(STOCKTWITS_MAX_RPS)

    @retry(
        retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
        wait=wait_exponential(multiplier=0.8, min=1, max=20),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def get(self, url: str, **kwargs) -> requests.Response:
        self._limiter.acquire()
        resp = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After")
            if ra:
                try:
                    time.sleep(min(float(ra), 30.0))
                except ValueError:
                    time.sleep(3 + random.random())
            else:
                time.sleep(2 + random.random())
            resp.raise_for_status()
        elif 500 <= resp.status_code < 600:
            resp.raise_for_status()
        return resp

# Global HTTP client instance (only created if REQUESTS_AVAILABLE)
http_client = None
if REQUESTS_AVAILABLE:
    try:
        http_client = HttpClient()
    except ImportError:
        http_client = None

# -----------------------------------------------------------------------------
# YAHOO FINANCE CLIENT
# -----------------------------------------------------------------------------

@dataclass
class YahooClient:
    ticker_symbol: str
    _ticker: yf.Ticker = field(init=False)
    _cache: Dict[str, Any] = field(default_factory=dict, init=False)
    _limiter: TokenBucket = field(default_factory=lambda: TokenBucket(YAHOO_MAX_RPS), init=False)

    def __post_init__(self) -> None:
        # IMPORTANT: do NOT pass a requests/session into yf.Ticker now
        self._ticker = yf.Ticker(self.ticker_symbol)

    def _throttled(self, fn_name: str, call) -> Any:
        if fn_name in self._cache:
            return self._cache[fn_name]
        # throttle before any yfinance call (since we can't inject a session)
        self._limiter.acquire()
        val = call()
        self._cache[fn_name] = val
        return val

    def _retryable(self, func, *args, **kwargs):
        @retry(
            retry=retry_if_exception_type(Exception),
            wait=wait_exponential(multiplier=0.8, min=1, max=20),
            stop=stop_after_attempt(6),
            reraise=True,
        )
        def wrapped():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # yfinance surfaces 429s and rate messages as generic Exceptions
                msg = str(e).lower()
                if "too many requests" in msg or "rate limit" in msg or "429" in msg:
                    time.sleep(1.5 + random.random())
                raise
        return wrapped()

    # Prefer fast_info: lighter-weight
    def fast_info(self) -> Dict[str, Any]:
        return self._throttled(
            "fast_info",
            lambda: self._retryable(lambda: dict(self._ticker.fast_info or {}))
        )

    def history(self, **kwargs) -> pd.DataFrame:
        key = f"history:{kwargs}"
        return self._throttled(key, lambda: self._retryable(self._ticker.history, **kwargs))

    def quarterly_financials(self) -> pd.DataFrame:
        return self._throttled(
            "quarterly_financials",
            lambda: self._retryable(lambda: self._ticker.quarterly_financials)
        )

    def options(self) -> List[str]:
        return self._throttled("options", lambda: self._retryable(lambda: list(self._ticker.options or [])))

    def option_chain(self, expiration: str):
        key = f"option_chain:{expiration}"
        return self._throttled(key, lambda: self._retryable(self._ticker.option_chain, expiration))

# -----------------------------------------------------------------------------
# FUNDAMENTAL ANALYSIS FUNCTIONS
# -----------------------------------------------------------------------------

def fundamental_score(
    data: Dict[str, Any],
    positive_growth_pct: Optional[float],
    earnings_date: Optional[str],
) -> Dict[str, Any]:
    """
    Evaluate fundamentals across 5 pillars and return a detailed result dict:
      {
        'status': 'PASS'|'FAIL',
        'score': int,
        'required': int,
        'pillars': {
            'profitability': {'pass': bool, 'reason': str},
            'growth':        {'pass': bool, 'reason': str},
            'balance_sheet': {'pass': bool, 'reason': str},
            'market_pos':    {'pass': bool, 'reason': str},
            'forward':       {'pass': bool, 'reason': str},
        }
      }
    """
    pillars: Dict[str, Dict[str, Any]] = {}

    # ----- Profitability -----
    pm = data.get("profit_margin")
    om = data.get("operating_margin")
    profit_ok = (pm or 0) >= MIN_PROFIT_MARGIN and (om or 0) >= MIN_OPER_MARGIN
    pillars["profitability"] = {
        "pass": profit_ok,
        "reason": (
            f"Profit margin={pm:.2%} (≥{MIN_PROFIT_MARGIN:.0%}) and "
            f"Operating margin={om:.2%} (≥{MIN_OPER_MARGIN:.0%})"
            if pm is not None and om is not None else
            "Missing profitability data"
        )
    }

    # ----- Growth -----
    qtr_growth = data.get("quarterly_revenue_change")
    pos_qtrs = positive_growth_pct if positive_growth_pct is not None else 0.0
    growth_ok = ((qtr_growth or 0) >= MIN_QTR_REV_GROWTH) or (pos_qtrs >= MIN_POSITIVE_QTRS)
    pillars["growth"] = {
        "pass": growth_ok,
        "reason": (
            f"QoQ revenue change={ (qtr_growth or 0):.2%} (≥{MIN_QTR_REV_GROWTH:.0%}) "
            f"or Positive quarters={pos_qtrs:.1f}% (≥{MIN_POSITIVE_QTRS:.0f}%)"
        )
    }

    # ----- Balance Sheet -----
    rev = data.get("revenue")
    debt = data.get("total_debt")
    ocf = data.get("operating_cash_flow")
    rev_debt = (rev / debt) if (rev is not None and debt not in (None, 0)) else None
    ocf_debt = (ocf / debt) if (ocf is not None and debt not in (None, 0)) else None
    bs_ok = (
        (rev_debt is not None and rev_debt >= MIN_REV_TO_DEBT) and
        (ocf_debt is not None and ocf_debt >= MIN_OCF_TO_DEBT)
    )
    pillars["balance_sheet"] = {
        "pass": bs_ok,
        "reason": (
            f"Revenue/Debt={rev_debt:.2f} (≥{MIN_REV_TO_DEBT:.2f}) and "
            f"OCF/Debt={ocf_debt:.2f} (≥{MIN_OCF_TO_DEBT:.2f})"
            if rev_debt is not None and ocf_debt is not None else
            "Missing leverage/coverage data"
        )
    }

    # ----- Market Position -----
    price = data.get("current_price")
    high_52 = data.get("high_52")
    decline = ((high_52 - price) / high_52) if (price not in (None, 0) and high_52 not in (None, 0)) else None
    market_ok = (decline is not None) and (decline <= MAX_DECLINE_FROM_HIGH)
    pillars["market_pos"] = {
        "pass": market_ok,
        "reason": (
            f"Decline from 52w high={decline:.1%} (≤{MAX_DECLINE_FROM_HIGH:.0%})"
            if decline is not None else
            "Missing price/high_52 to compute decline"
        )
    }

    # ----- Forward Outlook -----
    forward_ok = bool(earnings_date)
    pillars["forward"] = {
        "pass": forward_ok,
        "reason": "Upcoming earnings date available" if forward_ok else "No upcoming earnings date"
    }

    score = sum(1 for p in pillars.values() if p["pass"])
    status = "PASS" if score >= REQUIRED_PASS_COUNT else "FAIL"

    return {
        "status": status,
        "score": score,
        "required": REQUIRED_PASS_COUNT,
        "pillars": pillars,
    }

def fetch_company_data(ticker_symbol: str) -> Dict[str, Any]:
    """
    Uses fast_info + 1y history for robust 52w stats; guarded fundamentals.
    """
    yh = YahooClient(ticker_symbol)
    data: Dict[str, Any] = {}

    # ---- Prices via fast_info ----
    finfo = yh.fast_info()  # keys often: last_price, year_high, year_low
    current_price = finfo.get("last_price")
    if current_price is None:
        hist_1d = yh.history(period="1d")
        current_price = hist_1d["Close"].iloc[-1] if not hist_1d.empty else None
    data["current_price"] = current_price

    # ---- Robust 52w hi/lo + change from 1y history (works even when fast_info misses) ----
    try:
        h1y = yh.history(period="1y", interval="1d")
        closes = h1y["Close"].dropna() if not h1y.empty else pd.Series(dtype=float)
        if len(closes) >= 2:
            data["high_52"] = float(closes.max())
            data["low_52"]  = float(closes.min())
            first = float(closes.iloc[0])
            last  = float(closes.iloc[-1])
            data["week_52_change"] = (last / first - 1.0) if first > 0 else None
        else:
            # fall back to fast_info when history is too short
            data["high_52"] = finfo.get("year_high")
            data["low_52"]  = finfo.get("year_low")
            data["week_52_change"] = None
    except Exception:
        data["high_52"] = finfo.get("year_high")
        data["low_52"]  = finfo.get("year_low")
        data["week_52_change"] = None

    # ---- Quarterly revenue change ----
    profit_margin = None
    operating_margin = None
    revenue = None
    total_debt = None
    operating_cash_flow = None

    try:
        q_fin = yh.quarterly_financials()
        if isinstance(q_fin, pd.DataFrame) and "Total Revenue" in q_fin.index:
            revenues = pd.to_numeric(q_fin.loc["Total Revenue"], errors="coerce").dropna()
            if len(revenues) >= 2:
                data["quarterly_revenue_change"] = (revenues.iloc[0] - revenues.iloc[1]) / revenues.iloc[1]
            else:
                data["quarterly_revenue_change"] = None
        else:
            data["quarterly_revenue_change"] = None
    except Exception:
        data["quarterly_revenue_change"] = None

    # ---- Heavy fundamentals: try once; swallow on fail ----
    try:
        finfo_heavy = yh._retryable(lambda: dict(yh._ticker.get_info() or {}))
        profit_margin       = finfo_heavy.get("profitMargins")
        operating_margin    = finfo_heavy.get("operatingMargins")
        revenue             = finfo_heavy.get("totalRevenue")
        total_debt          = finfo_heavy.get("totalDebt")
        operating_cash_flow = finfo_heavy.get("operatingCashflow")
    except Exception:
        pass

    data["profit_margin"]       = profit_margin
    data["operating_margin"]    = operating_margin
    data["revenue"]             = revenue
    data["total_debt"]          = total_debt
    data["operating_cash_flow"] = operating_cash_flow

    return data

def get_social_sentiment(ticker_symbol: str):
    """
    Fetches recent messages from StockTwits for the given ticker symbol
    and computes a simple sentiment ratio.
    Returns (bullish_ratio, bullish_count, bearish_count)
    """
    if not REQUESTS_AVAILABLE or http_client is None:
        return None, 0, 0
        
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker_symbol}.json"
    try:
        response = http_client.get(url)
        if response.status_code != 200:
            print(f"Error fetching social sentiment: Received status code {response.status_code}")
            return None, 0, 0

        if not response.text.strip():
            print("Error fetching social sentiment: Response is empty.")
            return None, 0, 0

        data = response.json()
        messages = data.get("messages", [])
        bullish_count = 0
        bearish_count = 0
        for msg in messages:
            sentiment = msg.get("entities", {}).get("sentiment", {})
            if sentiment:
                basic = sentiment.get("basic")
                if basic == "Bullish":
                    bullish_count += 1
                elif basic == "Bearish":
                    bearish_count += 1
        total = bullish_count + bearish_count
        if total > 0:
            bullish_ratio = bullish_count / total
            return bullish_ratio, bullish_count, bearish_count
        else:
            return None, 0, 0
    except Exception as e:
        print("Error fetching social sentiment:", e)
        return None, 0, 0

def compute_positive_quarterly_revenue_growth(ticker_symbol: str) -> Optional[float]:
    """
    Computes the percentage of quarters (in the past 5 years) with positive revenue growth.
    Returns this percentage as a float, or None on failure.
    """
    yh = YahooClient(ticker_symbol)
    try:
        q_fin = yh.quarterly_financials()
        if not (isinstance(q_fin, pd.DataFrame) and "Total Revenue" in q_fin.index):
            print("Total Revenue not found in quarterly financials.")
            return None

        # Convert revenue series to numeric to avoid dtype issues
        revenue_series = q_fin.loc["Total Revenue"]
        revenue_series = pd.to_numeric(revenue_series, errors='coerce')
        revenue_series = revenue_series.sort_index()

        pct_change = revenue_series.pct_change()
        cutoff = pd.Timestamp.today() - pd.DateOffset(years=5)
        try:
            pct_change.index = pd.to_datetime(pct_change.index)
        except Exception:
            pass

        pct_change = pct_change[pct_change.index >= cutoff]
        total_quarters = pct_change.count()
        if total_quarters == 0:
            return None
        positive_quarters = (pct_change > 0).sum()
        percent_positive = positive_quarters / total_quarters * 100
        return float(percent_positive)
    except Exception as e:
        print("Error computing quarterly revenue growth:", e)
        return None

def get_upcoming_earnings_call(ticker_symbol: str) -> Optional[str]:
    """
    Fetch upcoming earnings date using yfinance (no external session).
    Returns YYYY-MM-DD or None.
    """
    ticker = yf.Ticker(ticker_symbol)  # DO NOT pass a requests session here
    try:
        cal = ticker.calendar
        earnings_date = None
        if isinstance(cal, dict):
            if "Earnings Date" in cal and cal["Earnings Date"]:
                earnings_date = cal["Earnings Date"][0]
        elif hasattr(cal, "empty") and not cal.empty:
            if "Earnings Date" in cal.index:
                earnings_date = cal.loc["Earnings Date"].values[0]

        if not earnings_date:
            ed = ticker.earnings_dates(limit=5)
            if hasattr(ed, "empty") and not ed.empty:
                ed['Earnings Date'] = pd.to_datetime(ed['Earnings Date'])
                future_dates = ed[ed['Earnings Date'] >= pd.Timestamp.today()]
                if not future_dates.empty:
                    earnings_date = future_dates.iloc[0]['Earnings Date']

        if earnings_date is not None:
            if hasattr(earnings_date, 'strftime'):
                return earnings_date.strftime("%Y-%m-%d")
            return pd.to_datetime(earnings_date).strftime("%Y-%m-%d")
        return None
    except Exception as e:
        print("Error fetching earnings call date:", e)
        return None

def evaluate_options(ticker_symbol: str, current_price: float, high_52: Optional[float]) -> Dict[str, Any]:
    """
    Checks the options chain for two expiration dates:
      - The expiration nearest to the end of the current year.
      - The first expiration in the new year.
    For each expiration, filters call options to show only those with strike prices
    at or up to $10 above the current stock price.
    Returns a dictionary with options data.
    """
    try:
        yh = YahooClient(ticker_symbol)
        expirations = yh.options()
        
        if not expirations:
            return {"error": "No options available for this ticker."}
    except Exception as e:
        return {"error": f"Error fetching options: {e}"}

    # Convert expiration strings to datetime objects
    exp_dates = []
    for exp in expirations:
        try:
            dt = pd.to_datetime(exp)
            exp_dates.append((exp, dt))
        except Exception:
            continue

    # Separate expirations into those in the current year and next year
    current_year = datetime.today().year
    current_year_exps = [exp for exp, dt in exp_dates if dt.year == current_year]
    next_year_exps = [exp for exp, dt in exp_dates if dt.year == current_year + 1]

    # Choose the expiration nearest the end of the current year (if available)
    exp_current = max(current_year_exps) if current_year_exps else None
    # Choose the first expiration in the new year (if available)
    exp_next = max(next_year_exps) if next_year_exps else None

    result = {
        "current_price": current_price,
        "strike_range": f"{current_price:.2f} - {current_price + 10:.2f}",
        "expirations": {}
    }

    def process_expiration(expiration: str):
        try:
            chain = yh.option_chain(expiration)
            calls = chain.calls
            
            filtered = calls[(calls['strike'] >= current_price) & (calls['strike'] <= current_price + 10)]
            
            if not filtered.empty:
                options_data = filtered[['contractSymbol', 'strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility']].to_dict('records')
                result["expirations"][expiration] = {
                    "options": options_data,
                    "count": len(filtered)
                }
            else:
                result["expirations"][expiration] = {
                    "options": [],
                    "count": 0
                }
        except Exception as e:
            result["expirations"][expiration] = {
                "error": str(e),
                "options": [],
                "count": 0
            }

    if exp_current:
        result["expirations"]["current_year"] = {"expiration": exp_current}
        process_expiration(exp_current)
    else:
        result["expirations"]["current_year"] = {"error": "No expiration dates available in the current year."}

    if exp_next:
        result["expirations"]["next_year"] = {"expiration": exp_next}
        process_expiration(exp_next)
    else:
        result["expirations"]["next_year"] = {"error": "No expiration dates available in the new year."}

    return result

# -----------------------------------------------------------------------------
# TECHNICAL INDICATORS
# -----------------------------------------------------------------------------

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Support/Resistance (20d) and RSI.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with additional indicator columns
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    # Support/Resistance calculation
    df["Support"] = df["Low"].rolling(window=20, min_periods=1).min()
    df["Resistance"] = df["High"].rolling(window=20, min_periods=1).max()

    # RSI Calculation with proper error handling
    try:
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        
        # Avoid division by zero
        rs = gain / (loss + 1e-10)
        df["RSI"] = 100 - (100 / (1 + rs))
    except Exception:
        # Fallback to NaN if calculation fails
        df["RSI"] = np.nan
    
    return df

def get_base_price(df: pd.DataFrame) -> float:
    """
    Calculate base price using support levels and RSI oversold conditions.
    
    Args:
        df: DataFrame with indicator data
        
    Returns:
        Calculated base price or NaN if calculation fails
    """
    if df.empty or len(df) < 20:
        return np.nan

    try:
        recent = df.tail(20)
        
        # Get support levels
        avg_support = recent["Support"].mean() if "Support" in recent else np.nan
        min_low = recent["Low"].min()
        
        # RSI-based entry point
        rsi_buy = np.nan
        if "RSI" in recent:
            oversold = recent[recent["RSI"] < 30]
            if not oversold.empty:
                rsi_buy = oversold["Close"].min()

        # Combine all possibilities
        possibilities = [p for p in [avg_support, min_low, rsi_buy] 
                        if not np.isnan(p)]
        
        if not possibilities:
            return np.nan
            
        return round(float(np.mean(possibilities)), 2)
        
    except Exception:
        return np.nan

# -----------------------------------------------------------------------------
# CUSTOM EXCEPTIONS
# -----------------------------------------------------------------------------

class StockDataError(Exception):
    """Custom exception for stock data related errors."""
    pass

class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass

# -----------------------------------------------------------------------------
# MAIN APPLICATION CLASS
# -----------------------------------------------------------------------------

class StockAnalyzerApp:
    """
    Main application class for the Stock and Crypto Technical Analyzer.
    
    Features:
    - Interactive technical analysis charts
    - Multiple moving averages
    - Support/Resistance levels
    - RSI analysis
    - Async data fetching
    - Data caching for performance
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.current_symbol: Optional[str] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.canvas: Optional[Any] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Fundamental analysis data
        self.fundamental_data: Optional[Dict[str, Any]] = None
        self.social_sentiment: Optional[Tuple] = None
        self.positive_growth_percent: Optional[float] = None
        self.earnings_date: Optional[str] = None
        self.fundamental_score: Optional[Dict[str, Any]] = None
        self.options_data: Optional[Dict[str, Any]] = None
        
        # UI components
        self.symbol_var: Optional[tk.StringVar] = None
        self.timeframe_var: Optional[tk.StringVar] = None
        self.ma_vars: Dict[int, tk.BooleanVar] = {}
        
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Setup the main user interface."""
        self.root.title("Comprehensive Stock and Crypto Analyzer - Technical + Fundamental Analysis")
        self.root.geometry("1200x1000")
        self.root.minsize(1000, 750)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Stock input section
        input_frame = ttk.LabelFrame(main_frame, text="Stock/Crypto Symbol Input", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="Enter Symbol (e.g., AAPL, BTC-USD, ETH-USD):", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        input_control_frame = ttk.Frame(input_frame)
        input_control_frame.pack(fill="x", pady=5)
        
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(input_control_frame, textvariable=self.symbol_var, 
                                     font=("Segoe UI", 12))
        self.symbol_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.symbol_entry.bind('<Return>', lambda e: self.analyze_stock())
        
        self.analyze_button = ttk.Button(input_control_frame, text="Analyze", 
                                        command=self.analyze_stock)
        self.analyze_button.pack(side="right")
        
        # Chart controls section
        controls_frame = ttk.LabelFrame(main_frame, text="Chart Controls", padding=10)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Timeframe selection
        timeframe_frame = ttk.Frame(controls_frame)
        timeframe_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(timeframe_frame, text="Timeframe:").pack(side="left", padx=(0, 10))
        self.timeframe_var = tk.StringVar(value="2y")
        
        # Timeframe mapping with better organization
        self.timeframe_map = {
            "1 Day": "1d",
            "5 Days": "5d", 
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "10 Years": "10y",
            "Max": "max"
        }
        
        self.timeframe_cb = ttk.Combobox(
            timeframe_frame,
            textvariable=self.timeframe_var,
            values=list(self.timeframe_map.keys()),
            state="readonly",
            width=12
        )
        self.timeframe_cb.pack(side="left", padx=(0, 20))
        self.timeframe_cb.set("2 Years")
        
        # Moving averages checkboxes
        ma_frame = ttk.Frame(controls_frame)
        ma_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(ma_frame, text="Moving Averages:").pack(side="left", padx=(0, 10))
        
        # Better organized MA periods
        ma_periods = [10, 20, 30, 50, 72, 100, 200, 400, 420]
        for period in ma_periods:
            var = tk.BooleanVar(value=(period in [50, 200]))  # Default to 50 and 200 MA
            self.ma_vars[period] = var
            cb = ttk.Checkbutton(ma_frame, text=f"{period} MA", variable=var)
            cb.pack(side="left", padx=(0, 8))
        
        # Update button
        update_frame = ttk.Frame(controls_frame)
        update_frame.pack(fill="x")
        
        self.update_button = ttk.Button(update_frame, text="Update Chart", 
                                      command=self.update_chart)
        self.update_button.pack(side="left")
        
        # Combined analysis frame (symbol info + fundamental analysis + options)
        self.analysis_frame = ttk.LabelFrame(main_frame, text="Stock Analysis, Fundamentals & Options", padding=10)
        self.analysis_frame.pack(fill="x", pady=(0, 5))
        
        # Chart frame
        self.chart_frame = ttk.Frame(main_frame)
        self.chart_frame.pack(fill="both", expand=True)
        
        # MA color mapping with better colors
        self.ma_color_map = {
            10: "#FF6B6B", 20: "#4ECDC4", 30: "#45B7D1", 50: "#96CEB4", 
            72: "#FFEAA7", 100: "#DDA0DD", 200: "#98D8C8", 400: "#F7DC6F", 420: "#FF9FF3"
        }
        
        # Validation patterns
        self.symbol_pattern = r'^[A-Za-z0-9\-\.]+$'
        
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate stock/crypto symbol format.
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        if not symbol or len(symbol) < 1 or len(symbol) > 20:
            return False
        return bool(re.match(self.symbol_pattern, symbol))
    
    def display_stock_info(self, ticker: str, stock_info: Any) -> None:
        """
        Display basic stock/crypto information in the combined analysis frame.
        
        Args:
            ticker: Stock/crypto symbol
            stock_info: yfinance Ticker object
        """
        # Clear existing info
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
            
        # Create main container with three columns
        main_container = ttk.Frame(self.analysis_frame)
        main_container.pack(fill="both", expand=True)
        
        # Left column for basic info
        left_frame = ttk.LabelFrame(main_container, text="Basic Information", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
        info_text = f"Symbol: {ticker.upper()}\n"
        
        try:
            if hasattr(stock_info, 'info') and stock_info.info:
                info = stock_info.info
                info_text += f"Name: {info.get('longName', info.get('shortName', 'N/A'))}\n"
                
                # Only show relevant info based on asset type
                if any(keyword in ticker.upper() for keyword in ['BTC', 'ETH', 'ADA', 'DOT']):
                    # Crypto info
                    info_text += f"Type: Cryptocurrency\n"
                    if info.get('marketCap'):
                        info_text += f"Market Cap: ${info.get('marketCap', 'N/A'):,}\n"
                else:
                    # Stock info
                    info_text += f"Sector: {info.get('sector', 'N/A')}\n"
                    info_text += f"Industry: {info.get('industry', 'N/A')}\n"
                    if info.get('marketCap'):
                        info_text += f"Market Cap: ${info.get('marketCap', 'N/A'):,}\n"
                    if info.get('trailingPE'):
                        info_text += f"P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
                
                # Common info for both
                if info.get('fiftyTwoWeekHigh'):
                    info_text += f"52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
                if info.get('fiftyTwoWeekLow'):
                    info_text += f"52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
            else:
                info_text += "Information: Limited data available\n"
        except Exception:
            info_text += "Information: Unable to load details\n"
            
        ttk.Label(left_frame, text=info_text, font=("Segoe UI", 9), justify="left").pack(anchor="w")
        
        # Middle column for fundamental analysis (will be split into two subframes)
        self.fundamental_subframe = ttk.LabelFrame(main_container, text="Fundamental Analysis", padding=5)
        self.fundamental_subframe.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        # Right column for options analysis (will be populated by display_options_analysis)
        self.options_subframe = ttk.LabelFrame(main_container, text="Options Chain", padding=5)
        self.options_subframe.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    def display_fundamental_analysis(self, ticker: str) -> None:
        """
        Display fundamental analysis results in the compact UI.
        
        Args:
            ticker: Stock/crypto symbol
        """
        # Check if the fundamental subframe exists
        if not hasattr(self, 'fundamental_subframe'):
            return
            
        # Clear existing fundamental analysis
        for widget in self.fundamental_subframe.winfo_children():
            widget.destroy()
            
        if not self.fundamental_data or not self.fundamental_score:
            ttk.Label(self.fundamental_subframe, text="Fundamental analysis\ndata not available", 
                     font=("Segoe UI", 10), foreground="orange").pack(anchor="w")
            return
        
        # Create two-column layout within fundamental analysis
        fundamental_container = ttk.Frame(self.fundamental_subframe)
        fundamental_container.pack(fill="both", expand=True)
        
        # Left column: 5-Pillar Analysis
        pillars_frame = ttk.LabelFrame(fundamental_container, text="5-Pillar Analysis", padding=3)
        pillars_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        # Right column: Financial Metrics
        metrics_frame = ttk.LabelFrame(fundamental_container, text="Financial Metrics", padding=3)
        metrics_frame.pack(side="right", fill="both", expand=True, padx=(3, 0))
        
        # Create scrollable frame for pillars analysis
        pillars_canvas = tk.Canvas(pillars_frame, height=220)
        pillars_scrollbar = ttk.Scrollbar(pillars_frame, orient="vertical", command=pillars_canvas.yview)
        pillars_scrollable_frame = ttk.Frame(pillars_canvas)
        
        pillars_scrollable_frame.bind(
            "<Configure>",
            lambda e: pillars_canvas.configure(scrollregion=pillars_canvas.bbox("all"))
        )
        
        pillars_canvas.create_window((0, 0), window=pillars_scrollable_frame, anchor="nw")
        pillars_canvas.configure(yscrollcommand=pillars_scrollbar.set)
        
        # Create scrollable frame for financial metrics
        metrics_canvas = tk.Canvas(metrics_frame, height=220)
        metrics_scrollbar = ttk.Scrollbar(metrics_frame, orient="vertical", command=metrics_canvas.yview)
        metrics_scrollable_frame = ttk.Frame(metrics_canvas)
        
        metrics_scrollable_frame.bind(
            "<Configure>",
            lambda e: metrics_canvas.configure(scrollregion=metrics_canvas.bbox("all"))
        )
        
        metrics_canvas.create_window((0, 0), window=metrics_scrollable_frame, anchor="nw")
        metrics_canvas.configure(yscrollcommand=metrics_scrollbar.set)
        
        # Fundamental Score Summary (display in both columns)
        score_text = f"Overall Score: {self.fundamental_score['status']} ({self.fundamental_score['score']}/{self.fundamental_score['required']})"
        score_color = "green" if self.fundamental_score['status'] == 'PASS' else "red"
        ttk.Label(pillars_scrollable_frame, text=score_text, font=("Segoe UI", 10, "bold"), 
                 foreground=score_color).pack(anchor="w", pady=(0, 5))
        
        # 5-Pillar Analysis (Left Column)
        for pillar_name, pillar_data in self.fundamental_score['pillars'].items():
            status_icon = "✅" if pillar_data['pass'] else "❌"
            pillar_display_name = pillar_name.replace('_', ' ').title()
            
            # Create a frame for each pillar
            pillar_frame = ttk.Frame(pillars_scrollable_frame)
            pillar_frame.pack(fill="x", pady=2)
            
            # Pillar name with status
            pillar_header = f"{status_icon} {pillar_display_name}"
            ttk.Label(pillar_frame, text=pillar_header, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            
            # Detailed reason with larger font
            reason_text = pillar_data['reason']
            if len(reason_text) > 45:  # Wrap long text
                # Split long text into multiple lines
                words = reason_text.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) > 45:
                        lines.append(current_line)
                        current_line = word
                    else:
                        current_line += " " + word if current_line else word
                if current_line:
                    lines.append(current_line)
                for line in lines:
                    ttk.Label(pillar_frame, text=f"  {line}", font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0))
            else:
                ttk.Label(pillar_frame, text=f"  {reason_text}", font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0))
        
        # Financial Metrics (Right Column)
        if self.fundamental_data:
            # Show detailed metrics with larger fonts
            if self.fundamental_data.get('profit_margin') is not None:
                pm = self.fundamental_data['profit_margin']
                pm_status = "✅" if pm >= MIN_PROFIT_MARGIN else "❌"
                ttk.Label(metrics_scrollable_frame, text=f"{pm_status} Profit Margin:", 
                         font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
                ttk.Label(metrics_scrollable_frame, text=f"  {pm:.2%} (≥{MIN_PROFIT_MARGIN:.0%})", 
                         font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
            
            if self.fundamental_data.get('operating_margin') is not None:
                om = self.fundamental_data['operating_margin']
                om_status = "✅" if om >= MIN_OPER_MARGIN else "❌"
                ttk.Label(metrics_scrollable_frame, text=f"{om_status} Operating Margin:", 
                         font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
                ttk.Label(metrics_scrollable_frame, text=f"  {om:.2%} (≥{MIN_OPER_MARGIN:.0%})", 
                         font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
            
            if self.fundamental_data.get('revenue') is not None and self.fundamental_data.get('total_debt') is not None:
                rev = self.fundamental_data['revenue']
                debt = self.fundamental_data['total_debt']
                if debt > 0:
                    rev_debt_ratio = rev / debt
                    rd_status = "✅" if rev_debt_ratio >= MIN_REV_TO_DEBT else "❌"
                    ttk.Label(metrics_scrollable_frame, text=f"{rd_status} Revenue/Debt:", 
                             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
                    ttk.Label(metrics_scrollable_frame, text=f"  {rev_debt_ratio:.2f} (≥{MIN_REV_TO_DEBT:.1f})", 
                             font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
            
            if self.fundamental_data.get('operating_cash_flow') is not None and self.fundamental_data.get('total_debt') is not None:
                ocf = self.fundamental_data['operating_cash_flow']
                debt = self.fundamental_data['total_debt']
                if debt > 0:
                    ocf_debt_ratio = ocf / debt
                    oc_status = "✅" if ocf_debt_ratio >= MIN_OCF_TO_DEBT else "❌"
                    ttk.Label(metrics_scrollable_frame, text=f"{oc_status} OCF/Debt:", 
                             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
                    ttk.Label(metrics_scrollable_frame, text=f"  {ocf_debt_ratio:.2f} (≥{MIN_OCF_TO_DEBT:.1f})", 
                             font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
            
            if self.fundamental_data.get('quarterly_revenue_change') is not None:
                qtr_growth = self.fundamental_data['quarterly_revenue_change']
                qg_status = "✅" if qtr_growth >= MIN_QTR_REV_GROWTH else "❌"
                ttk.Label(metrics_scrollable_frame, text=f"{qg_status} QoQ Growth:", 
                         font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
                ttk.Label(metrics_scrollable_frame, text=f"  {qtr_growth:.2%} (≥{MIN_QTR_REV_GROWTH:.0%})", 
                         font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
        
        # Growth Analysis with details (in metrics column)
        if self.positive_growth_percent is not None:
            pg_status = "✅" if self.positive_growth_percent >= MIN_POSITIVE_QTRS else "❌"
            ttk.Label(metrics_scrollable_frame, text=f"{pg_status} 5Y Positive Quarters:", 
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
            ttk.Label(metrics_scrollable_frame, text=f"  {self.positive_growth_percent:.1f}% (≥{MIN_POSITIVE_QTRS:.0f}%)", 
                     font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
        
        # Market Position Analysis (in metrics column)
        if self.fundamental_data and self.fundamental_data.get('current_price') and self.fundamental_data.get('high_52'):
            price = self.fundamental_data['current_price']
            high_52 = self.fundamental_data['high_52']
            decline = (high_52 - price) / high_52
            mp_status = "✅" if decline <= MAX_DECLINE_FROM_HIGH else "❌"
            ttk.Label(metrics_scrollable_frame, text=f"{mp_status} Decline from 52W High:", 
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
            ttk.Label(metrics_scrollable_frame, text=f"  {decline:.1%} (≤{MAX_DECLINE_FROM_HIGH:.0%})", 
                     font=("Segoe UI", 8)).pack(anchor="w", padx=(10, 0), pady=(0, 3))
        
        # Earnings Date (in metrics column)
        if self.earnings_date:
            ttk.Label(metrics_scrollable_frame, text=f"✅ Upcoming Earnings:", 
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
            ttk.Label(metrics_scrollable_frame, text=f"  {self.earnings_date}", 
                     font=("Segoe UI", 8), foreground="blue").pack(anchor="w", padx=(10, 0))
        
        # Social Sentiment (in metrics column)
        if self.social_sentiment and self.social_sentiment[0] is not None:
            sentiment, bullish, bearish = self.social_sentiment
            sentiment_color = "green" if sentiment > 0.6 else "orange" if sentiment > 0.4 else "red"
            ttk.Label(metrics_scrollable_frame, text=f"📱 Social Sentiment:", 
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
            ttk.Label(metrics_scrollable_frame, text=f"  {sentiment*100:.1f}% Bullish", 
                     font=("Segoe UI", 8), foreground=sentiment_color).pack(anchor="w", padx=(10, 0))
            ttk.Label(metrics_scrollable_frame, text=f"  ({bullish} bullish, {bearish} bearish)", 
                     font=("Segoe UI", 8), foreground=sentiment_color).pack(anchor="w", padx=(10, 0))
        
        # Pack the scrollable components
        pillars_canvas.pack(side="left", fill="both", expand=True)
        pillars_scrollbar.pack(side="right", fill="y")
        
        metrics_canvas.pack(side="left", fill="both", expand=True)
        metrics_scrollbar.pack(side="right", fill="y")
    
    def display_options_analysis(self, ticker: str) -> None:
        """
        Display options chain analysis in the right column of the three-panel layout.
        
        Args:
            ticker: Stock/crypto symbol
        """
        # Check if the options subframe exists
        if not hasattr(self, 'options_subframe'):
            return
            
        # Clear existing options analysis
        for widget in self.options_subframe.winfo_children():
            widget.destroy()
            
        if not self.options_data:
            ttk.Label(self.options_subframe, text="Options analysis\ndata not available", 
                     font=("Segoe UI", 8), foreground="orange").pack(anchor="w")
            return
        
        if "error" in self.options_data:
            ttk.Label(self.options_subframe, text=f"Options Error:\n{self.options_data['error']}", 
                     font=("Segoe UI", 8), foreground="red").pack(anchor="w")
            return
        
        # Create scrollable frame for options
        canvas = tk.Canvas(self.options_subframe, height=220)
        scrollbar = ttk.Scrollbar(self.options_subframe, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Options overview
        current_price = self.options_data.get('current_price', 0)
        strike_range = self.options_data.get('strike_range', 'N/A')
        ttk.Label(scrollable_frame, text=f"Price: ${current_price:.2f}", 
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Label(scrollable_frame, text=f"Range: {strike_range}", 
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        
        # Process each expiration
        exp_count = 0
        for exp_key, exp_data in self.options_data['expirations'].items():
            # Skip the metadata entries, only process actual expiration dates
            if exp_key in ['current_year', 'next_year']:
                continue
                
            if isinstance(exp_data, dict) and 'options' in exp_data:
                expiration_date = exp_key  # The key is the expiration date
                
                # Create frame for this expiration
                exp_frame = ttk.LabelFrame(scrollable_frame, text=f"Expiration: {expiration_date}", padding=3)
                exp_frame.pack(fill="x", pady=(0, 5) if exp_count == 0 else (5, 0))
                
                # Get the actual options data
                options_list = exp_data.get('options', [])
                count = exp_data.get('count', 0)
                
                if count > 0:
                    ttk.Label(exp_frame, text=f"{count} calls found:", 
                             font=("Segoe UI", 8, "bold")).pack(anchor="w")
                    
                    # Table header with bigger fonts
                    header_frame = ttk.Frame(exp_frame)
                    header_frame.pack(fill="x", pady=(2, 0))
                    ttk.Label(header_frame, text="Strike", font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
                    ttk.Label(header_frame, text="Last", font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
                    ttk.Label(header_frame, text="Bid", font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
                    ttk.Label(header_frame, text="Ask", font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
                    ttk.Label(header_frame, text="IV", font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
                    
                    # Options data (limit to 5 for compact display)
                    for option in options_list[:5]:
                        option_frame = ttk.Frame(exp_frame)
                        option_frame.pack(fill="x", pady=1)
                        
                        # Strike price
                        strike = option.get('strike', 0)
                        ttk.Label(option_frame, text=f"${strike:.0f}", font=("Segoe UI", 8), width=8).pack(side="left")
                        
                        # Last price
                        last_price = option.get('lastPrice', 0)
                        last_color = "green" if last_price > 0 else "gray"
                        ttk.Label(option_frame, text=f"${last_price:.2f}", font=("Segoe UI", 8), 
                                 foreground=last_color, width=8).pack(side="left")
                        
                        # Bid
                        bid = option.get('bid', 0)
                        bid_color = "green" if bid > 0 else "gray"
                        ttk.Label(option_frame, text=f"${bid:.2f}", font=("Segoe UI", 8), 
                                 foreground=bid_color, width=8).pack(side="left")
                        
                        # Ask
                        ask = option.get('ask', 0)
                        ask_color = "red" if ask > 0 else "gray"
                        ttk.Label(option_frame, text=f"${ask:.2f}", font=("Segoe UI", 8), 
                                 foreground=ask_color, width=8).pack(side="left")
                        
                        # Implied Volatility
                        iv = option.get('impliedVolatility', 0)
                        if iv and iv > 0:
                            iv_color = "orange" if iv > 0.5 else "blue"
                            ttk.Label(option_frame, text=f"{iv:.2f}", font=("Segoe UI", 8), 
                                     foreground=iv_color, width=8).pack(side="left")
                        else:
                            ttk.Label(option_frame, text="N/A", font=("Segoe UI", 8), 
                                     foreground="gray", width=8).pack(side="left")
                    
                    if count > 5:
                        ttk.Label(exp_frame, text=f"... {count - 5} more", 
                                 font=("Segoe UI", 8), foreground="gray").pack(anchor="w", pady=(2, 0))
                else:
                    ttk.Label(exp_frame, text="No options in range", 
                             font=("Segoe UI", 8), foreground="orange").pack(anchor="w")
                
                exp_count += 1
        
        if exp_count == 0:
            ttk.Label(scrollable_frame, text="No valid expirations found", 
                     font=("Segoe UI", 7), foreground="orange").pack(anchor="w")
        
        # Pack the scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def analyze_stock(self) -> None:
        """Main function to analyze the entered stock symbol (async)."""
        symbol = self.symbol_var.get().strip().upper()
        
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a stock/crypto symbol.")
            return
        
        # Validate symbol format
        if not self.validate_symbol(symbol):
            messagebox.showwarning("Invalid Symbol", 
                                 "Invalid symbol format. Use format like AAPL, BTC-USD, etc.")
            return
        
        # Disable button during analysis
        self.analyze_button.config(state="disabled", text="Loading...")
        
        # Start async analysis
        self.executor.submit(self._analyze_stock_async, symbol)
    
    def _analyze_stock_async(self, symbol: str) -> None:
        """
        Asynchronous stock analysis including both technical and fundamental analysis.
        
        Args:
            symbol: Stock/crypto symbol to analyze
        """
        try:
            # Check if yfinance is available
            if not YFINANCE_AVAILABLE:
                raise ImportError("yfinance is not available. Please install it with: pip install yfinance")
            
            # Validate symbol by trying to get stock info
            stock = yf.Ticker(symbol)
            
            # Test if we can get price data (with timeout)
            test_data = stock.history(period="5d")
            if test_data.empty:
                raise StockDataError(f"No price data found for symbol: {symbol}")
            
            # Fetch fundamental analysis data
            try:
                self.fundamental_data = fetch_company_data(symbol)
                self.social_sentiment = get_social_sentiment(symbol)
                self.positive_growth_percent = compute_positive_quarterly_revenue_growth(symbol)
                self.earnings_date = get_upcoming_earnings_call(symbol)
                
                # Calculate fundamental score
                self.fundamental_score = fundamental_score(
                    self.fundamental_data, 
                    self.positive_growth_percent, 
                    self.earnings_date
                )
                
                # Fetch options data if we have price data
                if self.fundamental_data and self.fundamental_data.get('current_price') and self.fundamental_data.get('high_52'):
                    self.options_data = evaluate_options(
                        symbol, 
                        self.fundamental_data['current_price'], 
                        self.fundamental_data.get('high_52')
                    )
                else:
                    self.options_data = None
                    
            except Exception as e:
                print(f"Warning: Could not fetch fundamental data: {e}")
                self.fundamental_data = None
                self.social_sentiment = None
                self.positive_growth_percent = None
                self.earnings_date = None
                self.fundamental_score = None
                self.options_data = None
            
            # Update UI in main thread
            self.root.after(0, self._on_analysis_success, symbol, stock)
            
        except StockDataError as e:
            self.root.after(0, self._on_analysis_error, str(e))
        except Exception as e:
            self.root.after(0, self._on_analysis_error, f"Error analyzing {symbol}: {str(e)}")
    
    def _on_analysis_success(self, symbol: str, stock: Any) -> None:
        """Handle successful analysis."""
        self.current_symbol = symbol
        self.display_stock_info(symbol, stock)
        self.display_fundamental_analysis(symbol)
        self.display_options_analysis(symbol)
        self.update_chart()
        self.analyze_button.config(state="normal", text="Analyze")
    
    def _on_analysis_error(self, error_msg: str) -> None:
        """Handle analysis error."""
        messagebox.showerror("Analysis Error", error_msg)
        self.analyze_button.config(state="normal", text="Analyze")
            
    def update_chart(self) -> None:
        """Update the chart with current settings (async)."""
        if not self.current_symbol:
            messagebox.showwarning("No Symbol", "Please enter and analyze a symbol first.")
            return
        
        # Disable button during update
        self.update_button.config(state="disabled", text="Updating...")
        
        # Start async chart update
        self.executor.submit(self._update_chart_async)
    
    def _update_chart_async(self) -> None:
        """Asynchronous chart update."""
        try:
            # Get timeframe
            period = self.timeframe_map[self.timeframe_var.get()]
            
            # Check cache first
            df = _data_cache.get(self.current_symbol, period)
            
            if df is None:
                # Check if yfinance is available
                if not YFINANCE_AVAILABLE:
                    raise ImportError("yfinance is not available. Please install it with: pip install yfinance")
                
                # Fetch data
                stock = yf.Ticker(self.current_symbol)
                df = stock.history(period=period)
                
                if df.empty:
                    raise StockDataError(f"No data for {self.current_symbol} in '{period}' timeframe.")
                
                # Cache the data
                _data_cache.set(self.current_symbol, period, df)
            
            # Prepare data
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.index.name = "Date"
            
            # Calculate indicators
            df_ind = calculate_indicators(df)
            self.current_df = df_ind
            
            # Update UI in main thread
            self.root.after(0, self._on_chart_success, df_ind)
            
        except Exception as e:
            self.root.after(0, self._on_chart_error, str(e))
    
    def _on_chart_success(self, df_ind: pd.DataFrame) -> None:
        """Handle successful chart update."""
        try:
            # Clear existing chart
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            
            # Check if charting libraries are available
            if not MATPLOTLIB_AVAILABLE or not MPLFINANCE_AVAILABLE:
                raise ImportError("Charting libraries not available. Please install matplotlib and mplfinance")
            
            # Calculate base price and levels
            base_price = get_base_price(df_ind)
            below_5p = round(base_price * 0.95, 2) if not np.isnan(base_price) else None
            
            # Get last values for legend
            last_support = df_ind["Support"].iloc[-1] if "Support" in df_ind and not df_ind.empty else np.nan
            last_resistance = df_ind["Resistance"].iloc[-1] if "Resistance" in df_ind and not df_ind.empty else np.nan
            last_rsi = df_ind["RSI"].iloc[-1] if "RSI" in df_ind and not df_ind.empty else np.nan
            
            # Build moving averages list
            mav_list = [period for period, var in self.ma_vars.items() if var.get()]
            
            # Create additional plots
            addplots = []
            if "Support" in df_ind and df_ind["Support"].notna().any():
                addplots.append(mpf.make_addplot(df_ind["Support"], color="green", linestyle="--", width=1.5))
            if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
                addplots.append(mpf.make_addplot(df_ind["Resistance"], color="red", linestyle="--", width=1.5))
            if not np.isnan(base_price):
                addplots.append(mpf.make_addplot([base_price] * len(df_ind), color="orange", linestyle="--", width=1.5))
            if below_5p:
                addplots.append(mpf.make_addplot([below_5p] * len(df_ind), color="purple", linestyle="--", width=1.5))
                
            # MA colors
            mav_colors = [self.ma_color_map[ma] for ma in mav_list]
            
            # Create the plot
            fig, axlist = mpf.plot(
                df_ind,
                type="candle",
                mav=mav_list if mav_list else None,
                mavcolors=mav_colors if mav_list else None,
                addplot=addplots or [],
                volume=True,
                style="charles",
                returnfig=True,
                figsize=(12, 8),
                tight_layout=True
            )
            
            # Add legend
            main_ax = axlist[0]
            legend_handles = []
            legend_labels = []
            
            # Add MA legends
            for ma in mav_list:
                color = self.ma_color_map[ma]
                legend_handles.append(Line2D([], [], color=color, linewidth=2, label=f"{ma}-day MA"))
                legend_labels.append(f"{ma}-day MA")
                
            # Add indicator legends
            if "Support" in df_ind and df_ind["Support"].notna().any():
                sup_label = f"Support (20d): ${last_support:.2f}" if not np.isnan(last_support) else "Support (20d)"
                legend_handles.append(Line2D([], [], color="green", linestyle="--", linewidth=1.5, label=sup_label))
                legend_labels.append(sup_label)
                
            if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
                res_label = f"Resistance (20d): ${last_resistance:.2f}" if not np.isnan(last_resistance) else "Resistance (20d)"
                legend_handles.append(Line2D([], [], color="red", linestyle="--", linewidth=1.5, label=res_label))
                legend_labels.append(res_label)
                
            if not np.isnan(base_price):
                bp_label = f"Base Price: ${base_price:.2f}"
                legend_handles.append(Line2D([], [], color="orange", linestyle="--", linewidth=1.5, label=bp_label))
                legend_labels.append(bp_label)
                
            if below_5p:
                b5_label = f"5% Below Base: ${below_5p:.2f}"
                legend_handles.append(Line2D([], [], color="purple", linestyle="--", linewidth=1.5, label=b5_label))
                legend_labels.append(b5_label)
                
            # Add RSI info to title
            current_price = df_ind["Close"].iloc[-1]
            title_text = f"{self.current_symbol} - Current: ${current_price:.2f}"
            if not np.isnan(last_rsi):
                title_text += f" | RSI: {last_rsi:.1f}"
            main_ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20)
            
            if legend_handles:
                main_ax.legend(legend_handles, legend_labels, loc="upper left", fontsize=9, framealpha=0.9)
                
            # Display chart
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Show analysis summary
            self.show_analysis_summary(df_ind, current_price, last_rsi, base_price)
            
            self.update_button.config(state="normal", text="Update Chart")
            
        except Exception as e:
            self._on_chart_error(f"Chart rendering error: {str(e)}")
    
    def _on_chart_error(self, error_msg: str) -> None:
        """Handle chart error."""
        messagebox.showerror("Chart Error", error_msg)
        self.update_button.config(state="normal", text="Update Chart")
            
    def show_analysis_summary(self, df_ind: pd.DataFrame, current_price: float, 
                            rsi: float, base_price: float) -> None:
        """
        Show a summary of the technical and fundamental analysis.
        
        Args:
            df_ind: DataFrame with indicator data
            current_price: Current stock/crypto price
            rsi: Current RSI value
            base_price: Calculated base price
        """
        summary = f"\n📊 Comprehensive Analysis Summary for {self.current_symbol}:\n"
        summary += f"Current Price: ${current_price:.2f}\n"
        
        # Technical Analysis
        summary += "\n🔧 Technical Analysis:\n"
        if not np.isnan(rsi):
            if rsi > 70:
                summary += f"RSI: {rsi:.1f} (Overbought ⚠️)\n"
            elif rsi < 30:
                summary += f"RSI: {rsi:.1f} (Oversold ✅)\n"
            else:
                summary += f"RSI: {rsi:.1f} (Neutral)\n"
                
        if not np.isnan(base_price):
            if current_price <= base_price:
                summary += f"Base Price: ${base_price:.2f} (Below Base - Potential Buy ✅)\n"
            else:
                summary += f"Base Price: ${base_price:.2f} (Above Base)\n"
                
        # Fundamental Analysis
        if self.fundamental_score:
            summary += "\n💰 Fundamental Analysis:\n"
            summary += f"Overall Score: {self.fundamental_score['status']} ({self.fundamental_score['score']}/{self.fundamental_score['required']})\n"
            
            for pillar_name, pillar_data in self.fundamental_score['pillars'].items():
                status_icon = "✅" if pillar_data['pass'] else "❌"
                summary += f"{status_icon} {pillar_name.replace('_', ' ').title()}\n"
        
        # Social Sentiment
        if self.social_sentiment and self.social_sentiment[0] is not None:
            sentiment, bullish, bearish = self.social_sentiment
            summary += f"\n📱 Social Sentiment: {sentiment*100:.1f}% Bullish ({bullish} bullish, {bearish} bearish)\n"
        
        # Options Analysis
        if self.options_data and "error" not in self.options_data:
            summary += "\n📈 Options Analysis:\n"
            total_options = sum(exp_data.get('count', 0) for exp_data in self.options_data['expirations'].values() 
                              if isinstance(exp_data, dict) and 'count' in exp_data)
            summary += f"Available Options: {total_options} call options in strike range {self.options_data['strike_range']}\n"
        elif self.options_data and "error" in self.options_data:
            summary += f"\n📈 Options Analysis: {self.options_data['error']}\n"
                
        # Print to console for now (can be enhanced with GUI summary later)
        print(summary)
    
    def cleanup(self) -> None:
        """Cleanup resources when application closes."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------

def main() -> None:
    """Main application entry point."""
    # Check dependencies first
    if not YFINANCE_AVAILABLE:
        messagebox.showerror("Missing Dependency", 
                           "yfinance is required but not installed.\n"
                           "Please install it with: pip install yfinance")
        return
    
    if not MATPLOTLIB_AVAILABLE or not MPLFINANCE_AVAILABLE:
        messagebox.showerror("Missing Dependencies", 
                           "Charting libraries are required but not installed.\n"
                           "Please install them with:\n"
                           "pip install matplotlib mplfinance")
        return
    
    try:
        root = tk.Tk()
        app = StockAnalyzerApp(root)
        
        # Set focus to symbol entry
        app.symbol_entry.focus()
        
        # Handle window closing
        def on_closing():
            app.cleanup()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"Application startup error: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()

