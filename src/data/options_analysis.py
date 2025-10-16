"""
Options analysis functions for stock evaluation
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

from ..data.yahoo_client import YahooClient


def evaluate_options(ticker_symbol: str, current_price: float, high_52: Optional[float]) -> Dict[str, Any]:
    """
    Checks the options chain for two expiration dates:
      - The expiration nearest to the end of the current year.
      - The first expiration in the new year.

    For each expiration, filters call options to show only those with strike prices
    at or up to $10 above the current stock price.

    Returns a dictionary with options data.

    Args:
        ticker_symbol: Stock symbol
        current_price: Current stock price
        high_52: 52-week high price (optional)
        
    Returns:
        Dictionary containing options analysis results
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
                    # Handle NaN values and ensure proper data types
                    bid_val = row.get('bid', 0)
                    ask_val = row.get('ask', 0)
                    last_price = row.get('lastPrice', 0)
                    
                    # Convert to float and handle NaN
                    try:
                        bid_val = float(bid_val) if not pd.isna(bid_val) and bid_val is not None else 0.0
                        ask_val = float(ask_val) if not pd.isna(ask_val) and ask_val is not None else 0.0
                        last_price = float(last_price) if not pd.isna(last_price) and last_price is not None else 0.0
                    except (ValueError, TypeError):
                        bid_val = ask_val = last_price = 0.0
                    
                    # If bid/ask are 0 but we have lastPrice, use lastPrice as estimate
                    if bid_val == 0.0 and ask_val == 0.0 and last_price > 0:
                        bid_val = last_price * 0.98  # Estimate bid as 2% below last price
                        ask_val = last_price * 1.02  # Estimate ask as 2% above last price
                    
                    option_dict = {
                        'contractSymbol': row.get('contractSymbol', ''),
                        'strike': float(row.get('strike', 0)) if not pd.isna(row.get('strike', 0)) else 0.0,
                        'lastPrice': last_price,
                        'bid': bid_val,
                        'ask': ask_val,
                        'impliedVolatility': float(row.get('impliedVolatility', 0)) if not pd.isna(row.get('impliedVolatility', 0)) else 0.0,
                        'volume': int(row.get('volume', 0)) if not pd.isna(row.get('volume', 0)) else 0,
                        'openInterest': int(row.get('openInterest', 0)) if not pd.isna(row.get('openInterest', 0)) else 0
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
