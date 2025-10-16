"""
Configuration constants for the Stock Analysis Application
"""

# API Configuration
YAHOO_MAX_RPS = 2.0  # Max requests per second for Yahoo Finance API

# Fundamental Analysis Thresholds
MIN_PROFIT_MARGIN = 0.10       # 10% profit margin
MIN_OPER_MARGIN = 0.10         # 10% operating margin
MIN_QTR_REV_GROWTH = 0.05      # 5% QoQ revenue growth
MIN_POSITIVE_QTRS = 60.0       # 60% of last 5y quarters positive
MIN_REV_TO_DEBT = 2.0          # Revenue / Total Debt
MIN_OCF_TO_DEBT = 0.50         # Operating Cash Flow / Total Debt
MAX_52W_DECLINE = 0.30         # 30% max decline from 52-week high

# Chart Configuration
CHART_CACHE_TTL = 60  # Cache charts for 60 seconds

# UI Configuration
CARD_WIDTH = 320
CARD_HEIGHT = 400
OPTIONS_TABLE_HEIGHT = 120
OPTIONS_TABLE_WIDTH = 280
