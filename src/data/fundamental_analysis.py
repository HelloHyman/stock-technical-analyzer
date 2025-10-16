"""
Fundamental analysis functions for stock evaluation
"""

import pandas as pd
from typing import Dict, Any, Optional

from ..config.constants import (
    MIN_PROFIT_MARGIN, MIN_OPER_MARGIN, MIN_QTR_REV_GROWTH,
    MIN_POSITIVE_QTRS, MIN_REV_TO_DEBT, MIN_OCF_TO_DEBT, MAX_52W_DECLINE
)
from ..data.yahoo_client import YahooClient


def fundamental_score(
    ticker_symbol: str,
    current_price: float,
    high_52: float,
    profit_margin: Optional[float],
    operating_margin: Optional[float],
    quarterly_revenue_growth: Optional[float],
    positive_growth_percent: Optional[float],
    revenue_to_debt: Optional[float],
    ocf_to_debt: Optional[float],
    earnings_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate fundamental analysis score based on multiple criteria.
    
    Args:
        ticker_symbol: Stock symbol
        current_price: Current stock price
        high_52: 52-week high price
        profit_margin: Profit margin ratio
        operating_margin: Operating margin ratio
        quarterly_revenue_growth: Quarterly revenue growth rate
        positive_growth_percent: Percentage of positive growth quarters
        revenue_to_debt: Revenue to debt ratio
        ocf_to_debt: Operating cash flow to debt ratio
        earnings_date: Upcoming earnings date (optional)
        
    Returns:
        Dictionary containing fundamental analysis results
    """
    
    pillars = {}
    
    # Profitability analysis
    profitability_ok = False
    if profit_margin is not None and operating_margin is not None:
        profitability_ok = (profit_margin >= MIN_PROFIT_MARGIN) and (operating_margin >= MIN_OPER_MARGIN)
    
    pillars["profitability"] = {
        "status": profitability_ok,
        "profit_margin": profit_margin,
        "operating_margin": operating_margin,
        "details": f"Profit margin={profit_margin:.2%} (≥{MIN_PROFIT_MARGIN:.0%}) and Operating margin={operating_margin:.2%} (≥{MIN_OPER_MARGIN:.0%})" if profit_margin is not None and operating_margin is not None else "Data not available"
    }
    
    # Growth analysis
    growth_ok = False
    if quarterly_revenue_growth is not None or positive_growth_percent is not None:
        growth_ok = ((quarterly_revenue_growth or 0) >= MIN_QTR_REV_GROWTH) or ((positive_growth_percent or 0) >= MIN_POSITIVE_QTRS)
    
    # Build details string safely
    growth_details = []
    if quarterly_revenue_growth is not None:
        growth_details.append(f"QoQ revenue change={quarterly_revenue_growth:.2%} (≥{MIN_QTR_REV_GROWTH:.0%})")
    if positive_growth_percent is not None:
        growth_details.append(f"Positive quarters={positive_growth_percent:.1f}% (≥{MIN_POSITIVE_QTRS:.0f}%)")
    
    pillars["growth"] = {
        "status": growth_ok,
        "quarterly_revenue_growth": quarterly_revenue_growth,
        "positive_growth_percent": positive_growth_percent,
        "details": " or ".join(growth_details) if growth_details else "Data not available"
    }
    
    # Balance sheet analysis
    balance_sheet_ok = False
    if revenue_to_debt is not None and ocf_to_debt is not None:
        balance_sheet_ok = (revenue_to_debt >= MIN_REV_TO_DEBT) and (ocf_to_debt >= MIN_OCF_TO_DEBT)
    
    # Build details string safely
    balance_details = []
    if revenue_to_debt is not None:
        balance_details.append(f"Revenue/Debt={revenue_to_debt:.2f} (≥{MIN_REV_TO_DEBT:.1f})")
    if ocf_to_debt is not None:
        balance_details.append(f"OCF/Debt={ocf_to_debt:.2f} (≥{MIN_OCF_TO_DEBT:.1f})")
    
    pillars["balance_sheet"] = {
        "status": balance_sheet_ok,
        "revenue_to_debt": revenue_to_debt,
        "ocf_to_debt": ocf_to_debt,
        "details": " and ".join(balance_details) if balance_details else "Data not available"
    }
    
    # Market position analysis
    market_position_ok = False
    decline_from_high = None
    
    if current_price and high_52 and high_52 > 0:
        decline_from_high = (high_52 - current_price) / high_52
        market_position_ok = decline_from_high <= MAX_52W_DECLINE
    
    pillars["market_position"] = {
        "status": market_position_ok,
        "decline_from_52w_high": decline_from_high,
        "details": f"Decline from 52w high={decline_from_high:.1%} (≥{-MAX_52W_DECLINE:.0%})" if decline_from_high is not None else "Data not available"
    }
    
    # Forward outlook - check if earnings date is available
    forward_ok = earnings_date is not None and earnings_date != ""
    pillars["forward"] = {
        "status": forward_ok,
        "earnings_date": earnings_date,
        "details": f"Upcoming earnings: {earnings_date}" if forward_ok else "No earnings date available"
    }
    
    # Calculate overall score (need 4 out of 5 to pass)
    passed_pillars = sum(1 for pillar in pillars.values() if pillar["status"])
    total_pillars = len(pillars)
    overall_score = "PASS" if passed_pillars >= 4 else "FAIL"
    
    return {
        "overall_score": overall_score,
        "score_breakdown": f"{passed_pillars}/{total_pillars}",
        "pillars": pillars,
        "current_price": current_price,
        "high_52": high_52
    }


def fetch_company_data(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetch comprehensive company data including fundamentals and options.
    
    Args:
        ticker_symbol: Stock symbol to analyze
        
    Returns:
        Dictionary containing all company data
    """
    yh = YahooClient(ticker_symbol)
    
    data: Dict[str, Any] = {}
    
    try:
        # Get basic company info
        info = yh.info()
        
        # Extract key financial metrics
        data['current_price'] = info.get('currentPrice', 0)
        data['market_cap'] = info.get('marketCap', 0)
        data['pe_ratio'] = info.get('trailingPE', 0)
        data['high_52'] = info.get('fiftyTwoWeekHigh', 0)
        data['low_52'] = info.get('fiftyTwoWeekLow', 0)
        data['profit_margin'] = info.get('profitMargins', 0)
        data['operating_margin'] = info.get('operatingMargins', 0)
        data['revenue_growth'] = info.get('revenueGrowth', 0)
        data['debt_to_equity'] = info.get('debtToEquity', 0)
        data['return_on_equity'] = info.get('returnOnEquity', 0)
        data['sector'] = info.get('sector', 'Unknown')
        data['industry'] = info.get('industry', 'Unknown')
        data['company_name'] = info.get('longName', ticker_symbol)
        
        # Calculate additional metrics
        if data.get('market_cap', 0) > 0:
            data['enterprise_value'] = data['market_cap'] + info.get('totalDebt', 0) - info.get('totalCash', 0)
        
        # Get cash flow data
        try:
            cash_flow = yh._ticker.cashflow
            if not cash_flow.empty:
                latest_cash_flow = cash_flow.iloc[0]
                data['operating_cash_flow'] = latest_cash_flow.get('Total Cash From Operating Activities', 0)
        except Exception:
            data['operating_cash_flow'] = 0
        
        # Get balance sheet data
        try:
            balance_sheet = yh._ticker.balance_sheet
            if not balance_sheet.empty:
                latest_balance = balance_sheet.iloc[0]
                data['total_debt'] = latest_balance.get('Total Debt', 0)
                data['total_cash'] = latest_balance.get('Cash And Cash Equivalents', 0)
        except Exception:
            data['total_debt'] = 0
            data['total_cash'] = 0
        
        # Calculate ratios
        if data.get('total_debt', 0) > 0:
            data['revenue_to_debt'] = (info.get('totalRevenue', 0) or 0) / data['total_debt']
            data['ocf_to_debt'] = data.get('operating_cash_flow', 0) / data['total_debt']
        else:
            data['revenue_to_debt'] = float('inf')
            data['ocf_to_debt'] = float('inf')
        
    except Exception as e:
        print(f"Error fetching company data: {e}")
        data = {'error': str(e)}
    
    return data


def compute_positive_quarterly_revenue_growth(ticker_symbol: str) -> Optional[float]:
    """
    Compute the percentage of quarters with positive revenue growth over the last 5 years.
    
    Args:
        ticker_symbol: Stock symbol
        
    Returns:
        Percentage of positive quarters (0-100) or None if error
    """
    try:
        yh = YahooClient(ticker_symbol)
        
        # Get quarterly financials
        quarterly_financials = yh._ticker.quarterly_financials
        
        if quarterly_financials.empty or 'Total Revenue' not in quarterly_financials.index:
            return None
        
        # Get revenue data
        revenue_data = quarterly_financials.loc['Total Revenue']
        
        # Calculate quarter-over-quarter growth
        growth_rates = []
        for i in range(1, len(revenue_data)):
            current_revenue = revenue_data.iloc[i-1]
            previous_revenue = revenue_data.iloc[i]
            
            if previous_revenue != 0 and not pd.isna(current_revenue) and not pd.isna(previous_revenue):
                growth_rate = (current_revenue - previous_revenue) / abs(previous_revenue)
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return None
        
        # Calculate percentage of positive quarters
        positive_quarters = sum(1 for rate in growth_rates if rate > 0)
        positive_percentage = (positive_quarters / len(growth_rates)) * 100
        
        return positive_percentage
        
    except Exception as e:
        print(f"Error computing positive quarterly revenue growth: {e}")
        return None


def get_upcoming_earnings_call(ticker_symbol: str) -> Optional[str]:
    """
    Get the upcoming earnings call date for a ticker.
    
    Args:
        ticker_symbol: Stock symbol
        
    Returns:
        Earnings call date string or None if not available
    """
    try:
        yh = YahooClient(ticker_symbol)
        
        # Get calendar data
        calendar = yh._ticker.calendar
        
        if calendar is not None:
            # Handle both dict and DataFrame formats
            if isinstance(calendar, dict):
                # Calendar is a dict with 'Earnings Date' key
                if 'Earnings Date' in calendar and calendar['Earnings Date']:
                    earnings_date = calendar['Earnings Date']
                    if isinstance(earnings_date, (list, tuple)) and len(earnings_date) > 0:
                        earnings_date = earnings_date[0]
                    if hasattr(earnings_date, 'strftime'):
                        return earnings_date.strftime('%Y-%m-%d')
                    return str(earnings_date)
            elif hasattr(calendar, 'empty') and not calendar.empty:
                # Calendar is a DataFrame
                earnings_dates = calendar.index
                if len(earnings_dates) > 0:
                    next_earnings = earnings_dates[0]
                    return next_earnings.strftime('%Y-%m-%d')
        
        return None
        
    except Exception as e:
        print("Error fetching earnings call date:", e)
        return None
