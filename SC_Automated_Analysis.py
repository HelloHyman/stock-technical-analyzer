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



import flet as ft
import threading

import time

import random

import asyncio
from functools import lru_cache

from typing import Dict, List, Optional, Tuple, Any

from concurrent.futures import ThreadPoolExecutor

from dataclasses import dataclass, field

from datetime import datetime

import base64
import io


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



# Check for charting libraries
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    print("Warning: plotly not available. Please install with: pip install plotly")
    PLOTLY_AVAILABLE = False

# Keep matplotlib for fallback if needed
try:

    import matplotlib.pyplot as plt

    from matplotlib.lines import Line2D

    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for Flet
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

    decline = ((price - high_52) / high_52) if (price not in (None, 0) and high_52 not in (None, 0)) else None

    market_ok = (decline is not None) and (decline >= -MAX_DECLINE_FROM_HIGH)

    pillars["market_pos"] = {

        "pass": market_ok,

        "reason": (

            f"Decline from 52w high={decline:.1%} (≥{-MAX_DECLINE_FROM_HIGH:.0%})"

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
        highs = h1y["High"].dropna() if not h1y.empty else pd.Series(dtype=float)
        lows = h1y["Low"].dropna() if not h1y.empty else pd.Series(dtype=float)

        if len(closes) >= 2:

            data["high_52"] = float(highs.max())  # Use High prices for true 52w high

            data["low_52"]  = float(lows.min())   # Use Low prices for true 52w low

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

            print(f"Note: Social sentiment API unavailable (status {response.status_code}) - continuing without it")
            return None, 0, 0



        if not response.text.strip():

            print("Note: Social sentiment data unavailable - continuing without it")
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

        print("Note: Social sentiment unavailable - continuing without it")
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

                # Extract options data with all available fields
                options_data = []
                for _, row in filtered.iterrows():
                    option_dict = {
                        'contractSymbol': row.get('contractSymbol', ''),
                        'strike': row.get('strike', 0),
                        'lastPrice': row.get('lastPrice', 0),
                        'bid': row.get('bid', 0),
                        'ask': row.get('ask', 0),
                        'impliedVolatility': row.get('impliedVolatility', 0),
                        'volume': row.get('volume', 0),
                        'openInterest': row.get('openInterest', 0)
                    }
                    options_data.append(option_dict)
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

    - Modern Flet-based UI
    """

    

    def __init__(self, page: ft.Page):
        """

        Initialize the application.

        

        Args:

            page: Flet page
        """

        self.page = page
        self.current_symbol: Optional[str] = None

        self.current_df: Optional[pd.DataFrame] = None

        self.chart_image: Optional[str] = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        

        # Fundamental analysis data

        self.fundamental_data: Optional[Dict[str, Any]] = None

        self.social_sentiment: Optional[Tuple] = None

        self.positive_growth_percent: Optional[float] = None

        self.earnings_date: Optional[str] = None

        self.fundamental_score: Optional[Dict[str, Any]] = None

        self.options_data: Optional[Dict[str, Any]] = None

        

        # UI components

        self.symbol_field: Optional[ft.TextField] = None
        self.timeframe_dropdown: Optional[ft.Dropdown] = None
        self.ma_checkboxes: Dict[int, ft.Checkbox] = {}
        
        # UI state management
        self.current_view = "input"  # input, loading, results
        self.main_column: Optional[ft.Column] = None
        self.loading_container: Optional[ft.Container] = None
        self.results_container: Optional[ft.Container] = None
        
        # Validation patterns
        self.symbol_pattern = r'^[A-Za-z0-9\-\.]+$'
        
        self.setup_page()
        self.setup_ui()

    
    def setup_page(self) -> None:
        """Setup the Flet page."""
        self.page.title = "Comprehensive Stock and Crypto Analyzer"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 1000
        self.page.window_min_width = 1000
        self.page.window_min_height = 750
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Set up theme
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            font_family="Segoe UI"
        )
        

    def setup_ui(self) -> None:

        """Setup the main user interface."""

        
        # Create main column
        self.main_column = ft.Column(
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Show initial input screen
        self.show_input_screen()
        
        # Add main column to page
        self.page.add(self.main_column)
    
    def show_input_screen(self) -> None:
        """Show the initial input screen."""
        self.current_view = "input"
        
        # Clear main column
        self.main_column.controls.clear()
        
        # Create centered input screen
        self.symbol_field = ft.TextField(
            label="Stock/Crypto Symbol",
            hint_text="e.g., AAPL, BTC-USD, ETH-USD",
            prefix_icon=ft.Icons.SEARCH,
            border=ft.InputBorder.OUTLINE,
            width=400,
            text_size=16,
            on_submit=self.analyze_stock
        )
        
        self.analyze_button = ft.ElevatedButton(
            text="Analyze",
            icon=ft.Icons.ANALYTICS,
            on_click=self.analyze_stock,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600
            ),
            width=200,
            height=50
        )
        
        # Create centered input screen
        input_screen = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=100),  # Top spacing
                    ft.Text(
                        "Stock & Crypto Analyzer",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_800
                    ),
                    ft.Text(
                        "Enter a stock or cryptocurrency symbol to get comprehensive analysis",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Container(height=40),
                    ft.Row(
                        controls=[self.symbol_field, self.analyze_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Supports: AAPL, GOOGL, MSFT, BTC-USD, ETH-USD, and more",
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_500
                    ),
                    ft.Container(height=100)  # Bottom spacing
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.main_column.controls.append(input_screen)
        self.page.update()
    
    def show_loading_screen(self, symbol: str) -> None:
        """Show loading screen during analysis."""
        self.current_view = "loading"
        
        # Clear main column
        self.main_column.controls.clear()
        
        # Create animated loading text
        self.loading_text = ft.Text(
            "🔄 Loading price data...",
            size=14,
            color=ft.Colors.BLUE_600,
            text_align=ft.TextAlign.CENTER
        )
        
        # Create loading screen
        loading_screen = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=100),
                    ft.ProgressRing(
                        width=100,
                        height=100,
                        stroke_width=8,
                        color=ft.Colors.BLUE_600
                    ),
                    ft.Container(height=30),
                    ft.Text(
                        f"Analyzing {symbol.upper()}...",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_800
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Fetching market data, calculating indicators, and generating analysis",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600
                    ),
                    ft.Container(height=40),
                    self.loading_text
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.main_column.controls.append(loading_screen)
        self.page.update()
        
        # Start animated loading sequence
        self.start_loading_animation()
    
    def start_loading_animation(self) -> None:
        """Start animated loading text sequence."""
        import threading
        import time
        
        def animate_loading():
            loading_messages = [
                "🔄 Loading price data...",
                "📊 Calculating technical indicators...",
                "💰 Analyzing fundamentals...",
                "📈 Fetching options data...",
                "📱 Checking social sentiment...",
                "🔍 Processing market trends...",
                "⚡ Generating analysis report...",
                "✨ Finalizing results..."
            ]
            
            for i, message in enumerate(loading_messages):
                if self.current_view != "loading":  # Stop if user navigated away
                    break
                
                # Update loading text
                self.loading_text.value = message
                self.loading_text.color = ft.Colors.BLUE_600 if i % 2 == 0 else ft.Colors.GREEN_600
                self.page.update()
                
                # Wait before next message (faster for demo)
                time.sleep(1.5)
        
        # Run animation in background thread
        threading.Thread(target=animate_loading, daemon=True).start()
    
    def show_results_screen(self, symbol: str) -> None:
        """Show the complete analysis results screen."""
        self.current_view = "results"
        
        # Clear main column
        self.main_column.controls.clear()
        
        # Initialize controls for results screen
        self.setup_results_controls()
        
        # Create header with symbol and back button
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Back to Input",
                        on_click=lambda e: self.show_input_screen()
                    ),
                    ft.Text(
                        f"Analysis Results - {symbol.upper()}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_800
                    ),
                    ft.Container(expand=True)  # Spacer
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_50
        )
        
        # Chart controls section - cleaner layout
        controls_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Chart Controls", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.timeframe_dropdown, 
                        self.update_button
                    ], spacing=20, alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=10),
                    ft.Text("Moving Averages:", size=14, weight=ft.FontWeight.BOLD),
                    # All MA checkboxes in a single horizontal row
                    ft.Row(
                        controls=[checkbox for checkbox in self.ma_checkboxes.values()],
                        spacing=10
                    )
                ], spacing=10),
                padding=20
            )
        )
        
        # Analysis section placeholder
        self.analysis_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Stock Analysis, Fundamentals & Options", 
                           size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=200)  # Placeholder for analysis content
                ], spacing=10),
                padding=20
            )
        )
        
        # Chart section placeholder
        self.chart_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Technical Analysis Chart",
                           size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=600,
                        width=None,  # Allow full width
                        expand=True
                    )  # Placeholder for chart
                ], spacing=10),
                padding=20,
                expand=True
            ),
            expand=True
        )
        
        # Add all sections to main column
        self.main_column.controls.extend([
            header,
            ft.Container(height=10),
            controls_card,
            ft.Container(height=10),
            self.analysis_card,
            ft.Container(height=10),
            self.chart_card
        ])
        
        self.page.update()
    
    def setup_results_controls(self) -> None:
        """Setup controls for the results screen."""
        # Chart controls section
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

        

        self.timeframe_dropdown = ft.Dropdown(
            label="Timeframe",
            options=[ft.dropdown.Option(key, key) for key in self.timeframe_map.keys()],
            value="2 Years",
            border=ft.InputBorder.OUTLINE,
            width=200
        )
        

        # Moving averages checkboxes

        ma_periods = [10, 20, 30, 50, 72, 100, 200, 400, 420]

        self.ma_checkboxes = {}
        ma_checkboxes_row = []
        
        for period in ma_periods:

            checkbox = ft.Checkbox(
                label=f"{period} MA",
                value=(period in [50, 200])  # Default to 50 and 200 MA
            )
            self.ma_checkboxes[period] = checkbox
            ma_checkboxes_row.append(checkbox)
        
        # Create rows of checkboxes
        self.ma_rows = []
        for i in range(0, len(ma_checkboxes_row), 3):
            row_checkboxes = ma_checkboxes_row[i:i+3]
            self.ma_rows.append(ft.Row(controls=row_checkboxes, spacing=20))
        
        self.update_button = ft.ElevatedButton(
            text="Update Chart",
            icon=ft.Icons.REFRESH,
            on_click=self.update_chart,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600
            )
        )
        

        # MA color mapping with better colors

        self.ma_color_map = {

            10: "#FF6B6B", 20: "#4ECDC4", 30: "#45B7D1", 50: "#96CEB4", 

            72: "#FFEAA7", 100: "#DDA0DD", 200: "#98D8C8", 400: "#F7DC6F", 420: "#FF9FF3"

        }

        

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

        # Create info text
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

            

        # Create three-column layout with symmetrical containers
        basic_info = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Basic Information", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Divider(height=2),
                    ft.Text(info_text, size=14, color=ft.Colors.GREY_700)
                ], spacing=10),
                padding=20,
                width=320,
                height=400
            ),
            expand=True
        )
        
        # Fundamental analysis placeholder
        self.fundamental_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("💰 Fundamental Analysis", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Divider(height=2),
                    ft.Container(height=300)  # Empty space for analysis content
                ], spacing=10),
                padding=20,
                width=320,
                height=400
            ),
            expand=True
        )
        
        # Options analysis placeholder
        self.options_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📈 Options Chain", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Divider(height=2),
                    ft.Container(height=300)  # Empty space for options data
                ], spacing=10),
                padding=20,
                width=320,
                height=400
            ),
            expand=True
        )
        
        # Create row with three cards
        analysis_row = ft.Row(
            controls=[basic_info, self.fundamental_card, self.options_card],
            spacing=10
        )
        
        # Update the analysis card content
        self.analysis_card.content.content.controls[1] = analysis_row
        self.page.update()
    

    def display_fundamental_analysis(self, ticker: str) -> None:

        """

        Display fundamental analysis results in the compact UI.

        

        Args:

            ticker: Stock/crypto symbol

        """

        # Check if the fundamental card exists
        if not hasattr(self, 'fundamental_card'):
            return

            

        if not self.fundamental_data or not self.fundamental_score:

            self.fundamental_card.content.content.controls[1] = ft.Text(
                "Fundamental analysis data not available", 
                size=12, 
                color=ft.Colors.ORANGE
            )
            self.page.update()
            return

        

        # Create fundamental analysis content with improved styling
        score_text = f"Overall Score: {self.fundamental_score['status']} ({self.fundamental_score['score']}/{self.fundamental_score['required']})"

        score_color = ft.Colors.GREEN if self.fundamental_score['status'] == 'PASS' else ft.Colors.RED
        
        # 5-Pillar Analysis with larger fonts
        pillars_content = []
        pillars_content.append(ft.Text(score_text, size=16, weight=ft.FontWeight.BOLD, color=score_color))
        pillars_content.append(ft.Divider(height=2))
        
        for pillar_name, pillar_data in self.fundamental_score['pillars'].items():

            status_icon = "✅" if pillar_data['pass'] else "❌"

            pillar_display_name = pillar_name.replace('_', ' ').title()

            

            pillar_text = f"{status_icon} {pillar_display_name}"
            pillars_content.append(ft.Text(pillar_text, size=14, weight=ft.FontWeight.BOLD))
            pillars_content.append(ft.Text(f"  {pillar_data['reason']}", size=12))
        
        # Financial Metrics with vertical stacking for each section
        metrics_content = []
        if self.fundamental_data:

            # Profitability metrics - vertical stacking
            profitability_section = []
            if self.fundamental_data.get('profit_margin') is not None:

                pm = self.fundamental_data['profit_margin']

                pm_status = "✅" if pm >= MIN_PROFIT_MARGIN else "❌"

                profitability_section.append(
                    ft.Text(f"{pm_status} Profit Margin: {pm:.2%}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                )
            

            if self.fundamental_data.get('operating_margin') is not None:

                om = self.fundamental_data['operating_margin']

                om_status = "✅" if om >= MIN_OPER_MARGIN else "❌"

                profitability_section.append(
                    ft.Text(f"{om_status} Operating Margin: {om:.2%}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                )
            
            if profitability_section:
                metrics_content.append(ft.Text("💰 Profitability:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                for item in profitability_section:
                    metrics_content.append(item)
                metrics_content.append(ft.Container(height=10))
            
            # Growth metrics - vertical stacking
            growth_section = []
            # Add any growth-related metrics here if available
            
            # Balance Sheet metrics - vertical stacking
            balance_section = []
            if self.fundamental_data.get('revenue') is not None and self.fundamental_data.get('total_debt') is not None:

                rev = self.fundamental_data['revenue']

                debt = self.fundamental_data['total_debt']

                if debt > 0:

                    rev_debt_ratio = rev / debt

                    rd_status = "✅" if rev_debt_ratio >= MIN_REV_TO_DEBT else "❌"

                    balance_section.append(
                        ft.Text(f"{rd_status} Revenue/Debt: {rev_debt_ratio:.2f}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
                    )
            
            if balance_section:
                metrics_content.append(ft.Text("📊 Balance Sheet:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                for item in balance_section:
                    metrics_content.append(item)
                metrics_content.append(ft.Container(height=10))
            
            # Market Position with 52-week decline percentage - vertical stacking
            market_section = []
            # Use the same data source as main analysis for consistency
            if (self.fundamental_data and 
                self.fundamental_data.get('current_price') is not None and 
                self.fundamental_data.get('high_52') is not None):
                
                current_price = self.fundamental_data['current_price']
                high_52 = self.fundamental_data['high_52']
                decline_pct = ((current_price - high_52) / high_52) * 100
                decline_color = ft.Colors.GREEN if decline_pct >= 0 else ft.Colors.RED
                market_section.append(
                    ft.Text(f"📈 52W Decline: {decline_pct:.1f}%", size=14, weight=ft.FontWeight.BOLD, color=decline_color)
                )
            
            if market_section:
                metrics_content.append(ft.Text("📊 Market Position:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                for item in market_section:
                    metrics_content.append(item)
                metrics_content.append(ft.Container(height=10))
            
            # Forward Outlook - vertical stacking
            forward_section = []
            if hasattr(self, 'earnings_date') and self.earnings_date:
                forward_section.append(
                    ft.Text(f"📅 Upcoming Earnings: {self.earnings_date}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700)
                )
            
            if forward_section:
                metrics_content.append(ft.Text("📊 Forward Outlook:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
                for item in forward_section:
                    metrics_content.append(item)
                metrics_content.append(ft.Container(height=10))
        
        # Social Sentiment
        if self.social_sentiment and self.social_sentiment[0] is not None:

            sentiment, bullish, bearish = self.social_sentiment

            sentiment_color = ft.Colors.GREEN if sentiment > 0.6 else ft.Colors.ORANGE if sentiment > 0.4 else ft.Colors.RED
            metrics_content.append(ft.Container(height=10))
            metrics_content.append(ft.Text(f"📱 Social Sentiment: {sentiment*100:.1f}% Bullish", size=14, weight=ft.FontWeight.BOLD, color=sentiment_color))
            metrics_content.append(ft.Text(f"  ({bullish} bullish, {bearish} bearish)", size=12, color=sentiment_color))
        
        # Create two-column layout: pillars on left, metrics on right
        analysis_content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(pillars_content, spacing=8, scroll=ft.ScrollMode.ADAPTIVE),
                    expand=True,
                    padding=10
                ),
                ft.Container(
                    content=ft.Column(metrics_content, spacing=8, scroll=ft.ScrollMode.ADAPTIVE),
                    expand=True,
                    padding=10
                )
            ],
            spacing=10
        )
        
        self.fundamental_card.content.content.controls[1] = analysis_content
        self.page.update()
    

    def display_options_analysis(self, ticker: str) -> None:

        """

        Display options chain analysis in the right column of the three-panel layout.

        

        Args:

            ticker: Stock/crypto symbol

        """

        # Check if the options card exists
        if not hasattr(self, 'options_card'):
            return

            

        if not self.options_data:

            self.options_card.content.content.controls[1] = ft.Text(
                "Options analysis data not available", 
                size=12, 
                color=ft.Colors.ORANGE
            )
            self.page.update()
            return

        

        if "error" in self.options_data:

            self.options_card.content.content.controls[1] = ft.Text(
                f"Options Error:\n{self.options_data['error']}", 
                size=12, 
                color=ft.Colors.RED
            )
            self.page.update()
            return

        

        # Create enhanced options content
        options_content = []
        
        # Current price and range info with explanation
        current_price = self.options_data.get('current_price', 0)

        strike_range = self.options_data.get('strike_range', 'N/A')

        
        options_content.append(ft.Text(f"💰 Current Price: ${current_price:.2f}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700))
        options_content.append(ft.Text(f"📊 Price Range: {strike_range}", size=14, color=ft.Colors.BLUE_700))
        options_content.append(ft.Text("(Range represents available strike prices)", size=12, color=ft.Colors.GREY_600, italic=True))
        options_content.append(ft.Divider(height=2))
        
        # LEAPS focus - show contracts 1 year out and beyond
        leaps_found = False
        options_content.append(ft.Text("🎯 LEAPS (Long-term Options)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800))
        options_content.append(ft.Container(height=10))
        
        # Process each expiration, focusing on long-term options
        expiration_containers = []
        
        for exp_key, exp_data in self.options_data['expirations'].items():

            # Skip the metadata entries, only process actual expiration dates

            if exp_key in ['current_year', 'next_year']:

                continue

                

            if isinstance(exp_data, dict) and 'options' in exp_data:

                expiration_date = exp_key  # The key is the expiration date

                

                # Get the actual options data

                options_list = exp_data.get('options', [])

                count = exp_data.get('count', 0)

                

                if count > 0:

                    # Create expiration container content
                    exp_content = []
                    exp_content.append(ft.Text(f"📅 {expiration_date}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700))
                    
                    # Add table headers (evenly distributed)
                    header_row = ft.Row([
                        ft.Text("Strike", size=12, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Text("Bid", size=12, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Text("Ask", size=12, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Text("IV", size=12, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Text("OI", size=12, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Text("Vol", size=12, weight=ft.FontWeight.BOLD, expand=True)
                    ], spacing=5)
                    exp_content.append(header_row)
                    
                    # Add divider line
                    exp_content.append(ft.Container(height=1, bgcolor=ft.Colors.GREY_400))
                    
                    # Show all options in scrollable format
                    for option in options_list:  # Show all options, no limit
                        strike = option.get('strike', 0)

                        bid = option.get('bid', 0)
                        ask = option.get('ask', 0)
                        iv = option.get('impliedVolatility', 0)
                        open_interest = option.get('openInterest', 0)
                        volume = option.get('volume', 0)
                        strike_color = ft.Colors.GREEN_700 if strike <= current_price else ft.Colors.BLUE_700
                        
                        option_row = ft.Row([
                            ft.Text(f"${strike:.0f}", size=11, weight=ft.FontWeight.BOLD, color=strike_color, expand=True),
                            ft.Text(f"${bid:.2f}", size=11, color=ft.Colors.GREY_700, expand=True),
                            ft.Text(f"${ask:.2f}", size=11, color=ft.Colors.GREY_700, expand=True),
                            ft.Text(f"{iv:.1%}" if iv and iv > 0 else "N/A", size=11, color=ft.Colors.ORANGE_700, expand=True),
                            ft.Text(f"{open_interest:,}" if open_interest > 0 else "0", size=11, color=ft.Colors.BLUE_700, expand=True),
                            ft.Text(f"{volume:,}" if volume > 0 else "0", size=11, color=ft.Colors.GREEN_700, expand=True)
                        ], spacing=5)
                        exp_content.append(option_row)
                    
                    # Create scrollable expiration container (shorter to fit options chain)
                    expiration_container = ft.Container(
                        content=ft.Column(
                            exp_content, 
                            spacing=4,
                            scroll=ft.ScrollMode.AUTO  # Make it scrollable
                        ),
                        padding=6,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        width=None,  # Adaptive width
                        height=200,  # Shorter height to fit options chain
                        expand=True  # Fill available space
                    )
                    expiration_containers.append(expiration_container)
                    
                    leaps_found = True
                    
                    if len(expiration_containers) >= 2:  # Limit to 2 expirations side by side
                        break
        
        # Add expirations side by side with adaptive sizing
        if expiration_containers:
            expirations_row = ft.Row(
                expiration_containers, 
                spacing=10,
                expand=True,  # Allow containers to expand
                alignment=ft.MainAxisAlignment.SPACE_EVENLY  # Distribute space evenly
            )
            options_content.append(expirations_row)
        
        if not leaps_found:
            options_content.append(ft.Text("No LEAPS contracts found", size=14, color=ft.Colors.ORANGE))
        
        # Create scrollable column
        options_column = ft.Column(options_content, spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        
        self.options_card.content.content.controls[1] = options_column
        self.page.update()
        
    def analyze_stock(self, e=None) -> None:
        """Main function to analyze the entered stock symbol (async)."""

        if self.symbol_field:
            symbol = self.symbol_field.value.strip().upper()
        else:
            return
        

        if not symbol:

            # Create a temporary snack bar
            snack_bar = ft.SnackBar(
                content=ft.Text("Please enter a stock/crypto symbol."),
                bgcolor=ft.Colors.ORANGE
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            return

        

        # Validate symbol format

        if not self.validate_symbol(symbol):

            # Create a temporary snack bar
            snack_bar = ft.SnackBar(
                content=ft.Text("Invalid symbol format. Use format like AAPL, BTC-USD, etc."),
                bgcolor=ft.Colors.RED
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            return

        

        # Show loading screen
        self.show_loading_screen(symbol)
        

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

            self.page.run_thread(self._on_analysis_success, symbol, stock)
            

        except StockDataError as e:

            self.page.run_thread(self._on_analysis_error, str(e))
        except Exception as e:

            self.page.run_thread(self._on_analysis_error, f"Error analyzing {symbol}: {str(e)}")
    

    def _on_analysis_success(self, symbol: str, stock: Any) -> None:

        """Handle successful analysis."""

        self.current_symbol = symbol

        
        # Show results screen first
        self.show_results_screen(symbol)
        
        # Then populate with data
        self.display_stock_info(symbol, stock)

        self.display_fundamental_analysis(symbol)

        self.display_options_analysis(symbol)

        self.update_chart()

    

    def _on_analysis_error(self, error_msg: str) -> None:

        """Handle analysis error."""

        # Show input screen again
        self.show_input_screen()
        
        # Create a temporary snack bar
        snack_bar = ft.SnackBar(
            content=ft.Text(error_msg),
            bgcolor=ft.Colors.RED
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
    
    def update_chart(self, e=None) -> None:
        """Update the chart with current settings (async)."""

        if not self.current_symbol:

            # Create a temporary snack bar
            snack_bar = ft.SnackBar(
                content=ft.Text("Please enter and analyze a symbol first."),
                bgcolor=ft.Colors.ORANGE
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            return

        

        # Disable button during update

        self.update_button.disabled = True
        self.update_button.text = "Updating..."
        self.page.update()
        

        # Start async chart update

        self.executor.submit(self._update_chart_async)

    

    def _update_chart_async(self) -> None:

        """Asynchronous chart update."""

        try:

            # Check if controls are initialized
            if not self.timeframe_dropdown:
                print("Chart controls not initialized - skipping chart update")
                return
                
            # Get timeframe

            period = self.timeframe_map[self.timeframe_dropdown.value]
            

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

            self.page.run_thread(self._on_chart_success, df_ind)
            

        except Exception as e:

            self.page.run_thread(self._on_chart_error, str(e))
    

    def _on_chart_success(self, df_ind: pd.DataFrame) -> None:

        """Handle successful chart update."""

        try:

            # Check if Plotly is available
            if not PLOTLY_AVAILABLE:
                raise ImportError("Plotly not available. Please install with: pip install plotly")
            
            # Calculate base price and levels
            base_price = get_base_price(df_ind)
            below_5p = round(base_price * 0.95, 2) if not np.isnan(base_price) else None
            
            # Get last values for legend
            last_support = df_ind["Support"].iloc[-1] if "Support" in df_ind and not df_ind.empty else np.nan
            last_resistance = df_ind["Resistance"].iloc[-1] if "Resistance" in df_ind and not df_ind.empty else np.nan
            last_rsi = df_ind["RSI"].iloc[-1] if "RSI" in df_ind and not df_ind.empty else np.nan
            
            # Build moving averages list
            mav_list = [period for period, checkbox in self.ma_checkboxes.items() if checkbox.value]
            
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
            main_ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20, color='black')
            
            if legend_handles:
                main_ax.legend(legend_handles, legend_labels, loc="upper left", fontsize=9, framealpha=0.9)
            
            # Convert chart to base64 for Flet
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            chart_image = base64.b64encode(buf.getvalue()).decode()
            buf.close()
            plt.close(fig)
            
            # Create and display Plotly chart
            chart_image = self.create_plotly_chart(df_ind)
            
            # Create legend box and display chart with legend
            legend_box = self.create_legend_box(df_ind, base_price)
            
            chart_and_legend = ft.Row([
                ft.Container(
                    content=ft.Image(
                        src_base64=chart_image,
                        width=None,  # Allow full width
                        height=1000,  # Match the new chart height
                        fit=ft.ImageFit.CONTAIN,
                        expand=True
                    ),
                    expand=True
                ),
                ft.Container(
                    content=legend_box,
                    width=220,  # Slightly wider for price values
                    padding=10
                )
            ], spacing=10)
            
            self.chart_card.content.content.controls[1] = chart_and_legend
            
            # Show analysis summary
            self.show_analysis_summary(df_ind, current_price, last_rsi, base_price)
            
            # Re-enable button
            self.update_button.disabled = False
            self.update_button.text = "Update Chart"
            self.page.update()
            
        except Exception as e:
            self._on_chart_error(f"Chart rendering error: {str(e)}")
    
    def _on_chart_error(self, error_msg: str) -> None:
        """Handle chart error."""
        # Create a temporary snack bar
        snack_bar = ft.SnackBar(
            content=ft.Text(error_msg),
            bgcolor=ft.Colors.RED
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        
        # Re-enable button
        self.update_button.disabled = False
        self.update_button.text = "Update Chart"
        self.page.update()
    
    def _on_chart_success(self, df_ind: pd.DataFrame) -> None:
        """Handle successful chart update."""
        try:
            # Check if Plotly is available
            if not PLOTLY_AVAILABLE:
                raise ImportError("Plotly not available. Please install with: pip install plotly")
            

            # Calculate base price and levels

            base_price = get_base_price(df_ind)

            below_5p = round(base_price * 0.95, 2) if not np.isnan(base_price) else None

            

            # Get last values for legend

            last_support = df_ind["Support"].iloc[-1] if "Support" in df_ind and not df_ind.empty else np.nan

            last_resistance = df_ind["Resistance"].iloc[-1] if "Resistance" in df_ind and not df_ind.empty else np.nan

            last_rsi = df_ind["RSI"].iloc[-1] if "RSI" in df_ind and not df_ind.empty else np.nan

            

            # Build moving averages list

            mav_list = [period for period, checkbox in self.ma_checkboxes.items() if checkbox.value]
            

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

            main_ax.set_title(title_text, fontsize=14, fontweight='bold', pad=20, color='black')
            

            if legend_handles:

                main_ax.legend(legend_handles, legend_labels, loc="upper left", fontsize=9, framealpha=0.9)

                

            # Convert chart to base64 for Flet
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            chart_image = base64.b64encode(buf.getvalue()).decode()
            buf.close()
            plt.close(fig)
            
            # Create and display Plotly chart
            chart_image = self.create_plotly_chart(df_ind)
            
            # Create legend box and display chart with legend
            legend_box = self.create_legend_box(df_ind, base_price)
            
            chart_and_legend = ft.Row([
                ft.Container(
                    content=ft.Image(
                        src_base64=chart_image,
                        width=None,  # Allow full width
                        height=1000,  # Match the new chart height
                        fit=ft.ImageFit.CONTAIN,
                        expand=True
                    ),
                    expand=True
                ),
                ft.Container(
                    content=legend_box,
                    width=220,  # Slightly wider for price values
                    padding=10
                )
            ], spacing=10)
            
            self.chart_card.content.content.controls[1] = chart_and_legend
            

            # Show analysis summary

            self.show_analysis_summary(df_ind, current_price, last_rsi, base_price)

            

            # Re-enable button
            self.update_button.disabled = False
            self.update_button.text = "Update Chart"
            self.page.update()
            

        except Exception as e:

            self._on_chart_error(f"Chart rendering error: {str(e)}")

    

    def _on_chart_error(self, error_msg: str) -> None:

        """Handle chart error."""

        # Create a temporary snack bar
        snack_bar = ft.SnackBar(
            content=ft.Text(error_msg),
            bgcolor=ft.Colors.RED
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        
        # Re-enable button
        self.update_button.disabled = False
        self.update_button.text = "Update Chart"
        self.page.update()
    
    def create_legend_box(self, df_ind: pd.DataFrame, base_price: float) -> ft.Container:
        """Create a separate legend box for the chart with price values."""
        legend_items = []
        
        # Get current price and last values
        current_price = df_ind['Close'].iloc[-1] if not df_ind.empty else 0
        last_support = df_ind["Support"].iloc[-1] if "Support" in df_ind and not df_ind.empty else np.nan
        last_resistance = df_ind["Resistance"].iloc[-1] if "Resistance" in df_ind and not df_ind.empty else np.nan
        
        # Add current price
        legend_items.append(
            ft.Row([
                ft.Container(width=20, height=3, bgcolor="black"),
                ft.Text(f"Current Price: ${current_price:.2f}", size=12, weight=ft.FontWeight.BOLD)
            ], spacing=8)
        )
        legend_items.append(ft.Divider(height=1))
        
        # Add moving averages with current values
        mav_list = [period for period, checkbox in self.ma_checkboxes.items() if checkbox.value]
        for ma in mav_list:
            color = self.ma_color_map[ma]
            ma_value = df_ind['Close'].rolling(window=ma).mean().iloc[-1] if len(df_ind) >= ma else np.nan
            legend_items.append(
                ft.Row([
                    ft.Container(width=20, height=3, bgcolor=color),
                    ft.Text(f"{ma}-day MA: ${ma_value:.2f}" if not np.isnan(ma_value) else f"{ma}-day MA: N/A", size=11)
                ], spacing=8)
            )
        
        if mav_list:
            legend_items.append(ft.Divider(height=1))
        
        # Add support/resistance lines with values
        if "Support" in df_ind and df_ind["Support"].notna().any() and not np.isnan(last_support):
            legend_items.append(
                ft.Row([
                    ft.Container(width=20, height=2, bgcolor="green"),
                    ft.Text(f"Support: ${last_support:.2f}", size=11)
                ], spacing=8)
            )
        
        if "Resistance" in df_ind and df_ind["Resistance"].notna().any() and not np.isnan(last_resistance):
            legend_items.append(
                ft.Row([
                    ft.Container(width=20, height=2, bgcolor="red"),
                    ft.Text(f"Resistance: ${last_resistance:.2f}", size=11)
                ], spacing=8)
            )
        
        # Add base price lines with values
        if not np.isnan(base_price):
            legend_items.append(
                ft.Row([
                    ft.Container(width=20, height=2, bgcolor="orange"),
                    ft.Text(f"Base Price: ${base_price:.2f}", size=11)
                ], spacing=8)
            )
            
            below_5p = round(base_price * 0.95, 2)
            legend_items.append(
                ft.Row([
                    ft.Container(width=20, height=2, bgcolor="purple"),
                    ft.Text(f"5% Below Base: ${below_5p:.2f}", size=11)
                ], spacing=8)
            )
        
        if not np.isnan(base_price):
            legend_items.append(ft.Divider(height=1))
        
        # Add volume legend
        legend_items.append(
            ft.Row([
                ft.Container(width=20, height=2, bgcolor="lightgreen"),
                ft.Text("Volume (Up)", size=11)
            ], spacing=8)
        )
        legend_items.append(
            ft.Row([
                ft.Container(width=20, height=2, bgcolor="lightcoral"),
                ft.Text("Volume (Down)", size=11)
            ], spacing=8)
        )
        
        # Create legend box
        return ft.Container(
            content=ft.Column([
                ft.Text("Legend", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                ft.Column(legend_items, spacing=5)
            ], spacing=8),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )

    def create_plotly_chart(self, df_ind: pd.DataFrame) -> str:
        """Create a Plotly chart and return base64 encoded image."""
        # Calculate base price and levels
        base_price = get_base_price(df_ind)
        below_5p = round(base_price * 0.95, 2) if not np.isnan(base_price) else None
        
        # Get last values
        last_support = df_ind["Support"].iloc[-1] if "Support" in df_ind and not df_ind.empty else np.nan
        last_resistance = df_ind["Resistance"].iloc[-1] if "Resistance" in df_ind and not df_ind.empty else np.nan
        last_rsi = df_ind["RSI"].iloc[-1] if "RSI" in df_ind and not df_ind.empty else np.nan
        current_price = df_ind["Close"].iloc[-1]
        
        # Build moving averages list
        mav_list = [period for period, checkbox in self.ma_checkboxes.items() if checkbox.value]
        
        # Create subplots with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f"{self.current_symbol} - ${current_price:.2f} | RSI: {last_rsi:.1f}" if not np.isnan(last_rsi) else f"{self.current_symbol} - ${current_price:.2f}", ""),
            row_heights=[0.7, 0.3]
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df_ind.index,
                open=df_ind['Open'],
                high=df_ind['High'],
                low=df_ind['Low'],
                close=df_ind['Close'],
                name="Price",
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add moving averages
        for ma in mav_list:
            color = self.ma_color_map[ma]
            ma_data = df_ind['Close'].rolling(window=ma).mean()
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=ma_data,
                    mode='lines',
                    name=f"{ma}-day MA",
                    line=dict(color=color, width=2),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Add support line
        if "Support" in df_ind and df_ind["Support"].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=df_ind["Support"],
                    mode='lines',
                    name=f"Support (20d): ${last_support:.2f}" if not np.isnan(last_support) else "Support (20d)",
                    line=dict(color="green", dash="dash", width=1.5),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Add resistance line
        if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=df_ind["Resistance"],
                    mode='lines',
                    name=f"Resistance (20d): ${last_resistance:.2f}" if not np.isnan(last_resistance) else "Resistance (20d)",
                    line=dict(color="red", dash="dash", width=1.5),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Add base price line
        if not np.isnan(base_price):
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=[base_price] * len(df_ind),
                    mode='lines',
                    name=f"Base Price: ${base_price:.2f}",
                    line=dict(color="orange", dash="dash", width=1.5),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Add 5% below base price line
        if below_5p:
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=[below_5p] * len(df_ind),
                    mode='lines',
                    name=f"5% Below Base: ${below_5p:.2f}",
                    line=dict(color="purple", dash="dash", width=1.5),
                    showlegend=True
                ),
                row=1, col=1
            )
        
            # Add volume chart with color coding (green for up, red for down)
            volume_colors = []
            for i in range(len(df_ind)):
                if i == 0:
                    volume_colors.append('rgba(158,202,225,0.6)')  # Default color for first bar
                else:
                    if df_ind['Close'].iloc[i] > df_ind['Close'].iloc[i-1]:
                        volume_colors.append('rgba(0,255,0,0.6)')  # Green for up
                    else:
                        volume_colors.append('rgba(255,0,0,0.6)')  # Red for down
            
            fig.add_trace(
                go.Bar(
                    x=df_ind.index,
                    y=df_ind['Volume'],
                    name="Volume",
                    marker_color=volume_colors,
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Update layout with larger chart and separate legend
        fig.update_layout(
            title=f"{self.current_symbol} Technical Analysis",
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14),
            height=800,
            showlegend=False,  # Hide legend from main chart
            margin=dict(l=50, r=50, t=80, b=50)  # Add margins for better spacing
        )
        
        # Update axes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        # Convert chart to image for Flet with larger size
        # Create a much larger chart image for better visibility
        chart_width = 2000  # Much larger width for better detail
        chart_height = 1000  # Increased height as well
            
        img_bytes = pio.to_image(fig, format="png", width=chart_width, height=chart_height, scale=3)
        return base64.b64encode(img_bytes).decode()
            

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



def main(page: ft.Page) -> None:
    """Main application entry point."""

    # Check dependencies first

    if not YFINANCE_AVAILABLE:

        snack_bar = ft.SnackBar(
            content=ft.Text("yfinance is required but not installed. Please install it with: pip install yfinance"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    

    if not PLOTLY_AVAILABLE:
        snack_bar = ft.SnackBar(
            content=ft.Text("Plotly is required but not installed. Please install it with: pip install plotly"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    

    try:

        app = StockAnalyzerApp(page)
        

        # Set focus to symbol field
        if app.symbol_field:
            app.symbol_field.focus()
        

        # Handle window closing

        def on_disconnect():
            app.cleanup()

        

        page.on_disconnect = on_disconnect
        

    except Exception as e:

        print(f"Application startup error: {e}")

        snack_bar = ft.SnackBar(
            content=ft.Text(f"Failed to start application: {e}"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


def main_entry():
    """Main entry point for the application"""
    try:
        ft.app(target=main)
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main_entry()


