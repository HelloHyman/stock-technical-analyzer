"""
Dependency checking and imports for the Stock Analysis Application
"""

# Check for optional dependencies
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    from plotly.offline import plot
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    sp = None
    plot = None

# Core dependencies (required)
import flet as ft
import pandas as pd
import numpy as np
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
import json
import requests

# Optional retry dependencies
try:
    from retry import retry, retry_if_exception_type
    RETRY_AVAILABLE = True
except ImportError:
    RETRY_AVAILABLE = False
    # Create dummy decorators
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def retry_if_exception_type(*args):
        return lambda x: False

try:
    from tenacity import wait_exponential, stop_after_attempt
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    # Create dummy functions
    def wait_exponential(*args, **kwargs):
        return lambda x: x
    def stop_after_attempt(*args):
        return lambda x: x
