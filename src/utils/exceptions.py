"""
Custom exceptions for the Stock Analysis Application
"""


class StockDataError(Exception):
    """Raised when there's an error fetching or processing stock data."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass
