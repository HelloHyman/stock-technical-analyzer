#!/usr/bin/env python3
"""
Automated Stock and Crypto Technical Analyzer
- Enter any stock/crypto symbol for technical analysis
- Interactive chart with moving averages and indicators
- Support/Resistance levels and RSI analysis
- Customizable timeframes and chart settings
- Optimized for fast startup and performance
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor

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
        
        # UI components
        self.symbol_var: Optional[tk.StringVar] = None
        self.timeframe_var: Optional[tk.StringVar] = None
        self.ma_vars: Dict[int, tk.BooleanVar] = {}
        
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Setup the main user interface."""
        self.root.title("Automated Stock and Crypto Technical Analyzer")
        self.root.geometry("1000x850")
        self.root.minsize(800, 600)
        
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
        
        # Stock info frame
        self.info_frame = ttk.LabelFrame(main_frame, text="Symbol Information", padding=10)
        self.info_frame.pack(fill="x", pady=(0, 10))
        
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
        Display basic stock/crypto information.
        
        Args:
            ticker: Stock/crypto symbol
            stock_info: yfinance Ticker object
        """
        # Clear existing info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
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
            
        ttk.Label(self.info_frame, text=info_text, font=("Segoe UI", 9), justify="left").pack(anchor="w")
        
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
        Asynchronous stock analysis.
        
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
        Show a summary of the technical analysis.
        
        Args:
            df_ind: DataFrame with indicator data
            current_price: Current stock/crypto price
            rsi: Current RSI value
            base_price: Calculated base price
        """
        summary = f"\n📊 Technical Analysis Summary for {self.current_symbol}:\n"
        summary += f"Current Price: ${current_price:.2f}\n"
        
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

