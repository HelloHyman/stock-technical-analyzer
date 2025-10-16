"""
Technical analysis functions for stock evaluation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy import stats


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for the given DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added technical indicators
    """
    df = df.copy()
    
    # Calculate moving averages
    for ma in [20, 50, 100, 200]:
        df[f'MA{ma}'] = df['Close'].rolling(window=ma).mean()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # Calculate Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Calculate support and resistance levels
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    
    # Calculate volume indicators
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    
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


def calculate_price_forecast(df_ind: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate 1-year price forecast based on 72-day MA trend from past 2 years.
    
    Args:
        df_ind: DataFrame with OHLCV data
        
    Returns:
        Dictionary with forecast data including predicted price and confidence
    """
    try:
        # Quick validation
        if df_ind.empty or len(df_ind) < 72:
            return {"predicted_price": np.nan, "confidence": 0, "trend_slope": 0, "current_ma72": np.nan}
        
        # Use last 500 days (approximately 2 years) for trend analysis
        lookback_days = min(500, len(df_ind))
        recent_data = df_ind.tail(lookback_days)
        
        # Calculate 72-day moving average
        if len(recent_data) >= 72:
            ma72_values = recent_data['Close'].rolling(window=72, min_periods=36).mean()
        else:
            # For short data, use what we have
            ma72_values = recent_data['Close'].expanding(min_periods=1).mean()
        
        # Remove NaN values
        valid_indices = ~ma72_values.isna()
        if valid_indices.sum() < 20:
            return {"predicted_price": np.nan, "confidence": 0, "trend_slope": 0, "current_ma72": np.nan}
        
        # Get valid data - vectorized operations
        x = np.arange(valid_indices.sum())
        y = ma72_values[valid_indices].values
        
        # Use numpy polyfit for linear regression (faster than scipy)
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Quick R-squared calculation
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Get current MA72 value
        current_ma72 = float(ma72_values.iloc[-1])
        
        # Get current price
        current_price = float(df_ind['Close'].iloc[-1])
        
        # Calculate price to MA72 ratio
        price_to_ma_ratio = current_price / current_ma72 if current_ma72 > 0 else 1.0
        
        # Project 252 trading days (1 year) into the future for MA72
        predicted_ma72 = slope * (len(x) + 252) + intercept
        
        # Apply the ratio to get predicted price
        predicted_price = predicted_ma72 * price_to_ma_ratio
        
        # Calculate confidence based on R-squared
        confidence = min(95.0, max(10.0, r_squared * 100))
        
        return {
            "predicted_price": float(predicted_price),
            "confidence": float(confidence),
            "trend_slope": float(slope),
            "current_ma72": float(current_ma72),
            "current_price": float(current_price),
            "price_change_pct": float(((predicted_price - current_price) / current_price) * 100)
        }
        
    except Exception as e:
        print(f"Forecast calculation error: {e}")
        return {"predicted_price": np.nan, "confidence": 0, "trend_slope": 0, "current_ma72": np.nan}
