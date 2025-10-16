"""
Main application class for the Stock Analysis Application
"""

import flet as ft
import threading
import time
import re
import pandas as pd
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import signal
import sys
import atexit

from ..config.constants import CARD_WIDTH, CARD_HEIGHT, OPTIONS_TABLE_HEIGHT, OPTIONS_TABLE_WIDTH
from ..config.dependencies import YFINANCE_AVAILABLE, PLOTLY_AVAILABLE
from ..data.yahoo_client import YahooClient
from ..data.fundamental_analysis import (
    fundamental_score, fetch_company_data, 
    compute_positive_quarterly_revenue_growth, get_upcoming_earnings_call
)
from ..data.options_analysis import evaluate_options
from ..data.technical_analysis import calculate_indicators, get_base_price, calculate_price_forecast
from ..utils.cache import DataCache


class StockAnalyzerApp:
    """
    Main application class for the Stock Analysis Application.
    """

    def __init__(self, page: ft.Page) -> None:
        """Initialize the application."""
        self.page = page
        
        # Data storage
        self.current_symbol: Optional[str] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.chart_image: Optional[str] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.executor_shutdown = False  # Flag to prevent submitting tasks after shutdown
        
        # Chart caching for performance
        self.chart_cache: Dict[str, str] = {}  # Cache chart images by symbol+timeframe+settings
        self.chart_cache_timestamp: Dict[str, float] = {}
        self.chart_cache_ttl = 60  # Cache for 60 seconds
        
        # Data cache
        self.data_cache = DataCache(ttl_seconds=300)  # 5 minutes cache
        
        # Analysis results
        self.fundamental_data: Optional[Dict[str, Any]] = None
        self.social_sentiment: Optional[Dict[str, Any]] = None
        self.positive_growth_percent: Optional[float] = None
        self.earnings_date: Optional[str] = None
        self.fundamental_score: Optional[Dict[str, Any]] = None
        self.options_data: Optional[Dict[str, Any]] = None
        self.forecast_data: Optional[Dict[str, Any]] = None  # Cache for forecast
        
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
        """Setup the main page configuration."""
        self.page.title = "Stock & Crypto Automated Analysis"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_resizable = True
        # self.page.window_center()  # Removed - deprecated in current Flet version
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.fonts = {
            "Roboto Mono": "RobotoMono-Regular.ttf",
        }
        self.page.theme = ft.Theme(
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
            text="Analyze Stock",
            icon=ft.Icons.ANALYTICS,
            on_click=self.analyze_stock,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        input_screen = ft.Container(
            content=ft.Column([
                ft.Container(height=50),  # Top spacing
                ft.Text(
                    "Stock & Crypto Automated Analysis",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Comprehensive analysis with fundamentals, options, and technical indicators",
                    size=16,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                ft.Row([
                    self.symbol_field,
                    self.analyze_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=30),
                ft.Text(
                    "Enter a stock or crypto symbol to get started",
                    size=14,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
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
            content=ft.Column([
                ft.Container(height=100),
                ft.ProgressRing(
                    width=50,
                    height=50,
                    stroke_width=4,
                    color=ft.Colors.BLUE_600
                ),
                ft.Container(height=20),
                ft.Text(
                    f"Analyzing {symbol.upper()}...",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=10),
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
        
        loading_messages = [
            "🔄 Loading price data...",
            "📊 Fetching fundamentals...",
            "📈 Analyzing options chain...",
            "🔍 Calculating technical indicators...",
            "📋 Generating analysis report..."
        ]
        
        def animate_loading():
            for i, message in enumerate(loading_messages):
                if hasattr(self, 'loading_text') and self.loading_text:
                    self.loading_text.value = message
                    self.page.update()
                time.sleep(1.5)
        
        # Run animation in background thread
        threading.Thread(target=animate_loading, daemon=True).start()

    def analyze_stock(self, e=None) -> None:
        """Main function to analyze the entered stock symbol (async)."""
        if self.symbol_field:
            symbol = self.symbol_field.value.strip().upper()
            
            if not symbol:
                self.show_error("Please enter a stock symbol")
                return
            
            if not re.match(self.symbol_pattern, symbol):
                self.show_error("Invalid symbol format. Use letters, numbers, hyphens, and dots only.")
                return
        
        # Show loading screen
        self.show_loading_screen(symbol)
        
        # Start async analysis
        if not self.executor_shutdown:
            try:
                self.executor.submit(self._analyze_stock_async, symbol)
            except RuntimeError:
                # Executor might be shut down, run synchronously as fallback
                self._analyze_stock_async(symbol)
        else:
            # Executor is shut down, run synchronously
            self._analyze_stock_async(symbol)

    def cleanup(self) -> None:
        """Cleanup resources when application closes."""
        try:
            print("Starting cleanup process...")
            
            # Stop any running threads or background tasks
            if hasattr(self, 'executor') and self.executor:
                try:
                    print("Shutting down thread executor...")
                    self.executor_shutdown = True  # Set flag to prevent new submissions
                    self.executor.shutdown(wait=True)
                    print("Thread executor shut down successfully.")
                except Exception as e:
                    print(f"Error shutting down executor gracefully: {e}")
                    self.executor_shutdown = True  # Set flag even if shutdown fails
                    try:
                        self.executor.shutdown(wait=False)
                        print("Thread executor force-shut down.")
                    except Exception as e2:
                        print(f"Error force-shutting down executor: {e2}")
            
            # Clear any cached data
            if hasattr(self, 'chart_cache'):
                self.chart_cache.clear()
                print("Chart cache cleared.")
            
            if hasattr(self, 'chart_cache_timestamp'):
                self.chart_cache_timestamp.clear()
                print("Chart cache timestamps cleared.")
            
            # Reset application state
            self.current_symbol = None
            self.current_df = None
            self.chart_image = None
            self.fundamental_data = None
            self.options_data = None
            self.executor_shutdown = False  # Reset flag for potential restart
            
            print("Application state reset.")
            print("Cleanup completed successfully.")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Don't re-raise the exception to avoid crash during shutdown

    def _analyze_stock_async(self, symbol: str) -> None:
        """Asynchronous stock analysis including both technical and fundamental analysis."""
        try:
            # Check if yfinance is available
            if not YFINANCE_AVAILABLE:
                raise ImportError("yfinance is not available. Please install it with: pip install yfinance")
            
            # Validate symbol by trying to get stock info
            stock = YahooClient(symbol)
            
            # Test if we can get price data
            test_data = stock.history(period="5d")
            if test_data.empty:
                raise Exception(f"No price data found for symbol: {symbol}")
            
            # Fetch fundamental analysis data
            self.fundamental_data = fetch_company_data(symbol)
            
            if 'error' in self.fundamental_data:
                raise Exception(f"Error fetching fundamental data: {self.fundamental_data['error']}")
            
            # Get positive growth percentage
            self.positive_growth_percent = compute_positive_quarterly_revenue_growth(symbol)
            
            # Get earnings date
            self.earnings_date = get_upcoming_earnings_call(symbol)
            
            # Calculate fundamental score
            self.fundamental_score = fundamental_score(
                symbol,
                self.fundamental_data.get('current_price', 0),
                self.fundamental_data.get('high_52', 0),
                self.fundamental_data.get('profit_margin'),
                self.fundamental_data.get('operating_margin'),
                self.fundamental_data.get('revenue_growth'),
                self.positive_growth_percent,
                self.fundamental_data.get('revenue_to_debt'),
                self.fundamental_data.get('ocf_to_debt'),
                self.earnings_date  # Add earnings date parameter
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
                
            # Update UI in main thread
            self.page.run_thread(lambda: self._on_analysis_success(symbol, stock))
            
        except Exception as e:
            print(f"Warning: Could not fetch fundamental data: {e}")
            self.fundamental_data = None
            self.social_sentiment = None
            self.positive_growth_percent = None
            self.earnings_date = None
            self.fundamental_score = None
            self.options_data = None

    def _on_analysis_success(self, symbol: str, stock) -> None:
        """Handle successful analysis."""
        try:
            self.current_symbol = symbol
            
            # Clear cached forecast data for new stock
            self.forecast_data = None
            self._last_forecast_key = None  # Clear forecast cache key
            self._initial_chart_loaded = False  # Reset flag for new stock
            
            # Show results screen first
            self.show_results_screen(symbol)
            
            # Then populate with data - each in try-catch so one failure doesn't break others
            try:
                self.display_stock_info(symbol, stock)
            except Exception as e:
                print(f"Error displaying stock info: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                self.display_fundamental_analysis(symbol)
            except Exception as e:
                print(f"Error displaying fundamental analysis: {e}")
                import traceback
                traceback.print_exc()
            
            # Display options first (will show "Calculating..." for forecast)
            try:
                self.display_options_analysis(symbol)
            except Exception as e:
                print(f"Error displaying options analysis: {e}")
                import traceback
                traceback.print_exc()
            
            # UPDATE CHART - This calculates the forecast asynchronously
            # When chart completes, it will refresh the options display with forecast
            try:
                self.update_chart()
            except Exception as e:
                print(f"Error updating chart: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"Fatal error in _on_analysis_success: {e}")
            import traceback
            traceback.print_exc()

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
                        on_click=lambda e: self.show_input_screen(),
                        tooltip="Back to search"
                    ),
                    ft.Text(
                        f"Analysis Results: {symbol.upper()}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_800,
                        expand=True
                    ),
                    ft.Container(width=48)  # Spacer for alignment
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10
        )
        
        # Controls card for chart settings
        controls_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Chart Controls", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("Timeframe:", size=14),
                        self.timeframe_dropdown,
                        self.update_button
                    ], spacing=20, alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=10),
                    ft.Text("Moving Averages:", size=14, weight=ft.FontWeight.BOLD),
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
                        content=ft.Text("Loading chart...", size=14),
                        height=400,
                        alignment=ft.alignment.center,
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
            "Max": "max"
        }
        
        self.timeframe_dropdown = ft.Dropdown(
            label="Timeframe",
            value="2 Years",
            options=[ft.dropdown.Option(key) for key in self.timeframe_map.keys()],
            width=150,
            on_change=self.update_chart
        )
        
        # Moving averages checkboxes
        ma_periods = [10, 20, 30, 50, 72, 100, 200, 400, 420]
        self.ma_checkboxes = {}
        
        for period in ma_periods:
            checkbox = ft.Checkbox(
                label=f"{period} MA",
                value=(period in [50, 200])  # Default to 50 and 200 MA
            )
            self.ma_checkboxes[period] = checkbox
        
        self.update_button = ft.ElevatedButton(
            text="Update Chart",
            icon=ft.Icons.REFRESH,
            on_click=self.update_chart,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        )
        
        # MA color mapping with better colors
        self.ma_color_map = {
            10: "#FF6B6B", 20: "#4ECDC4", 30: "#45B7D1", 50: "#96CEB4", 
            72: "#FFEAA7", 100: "#DDA0DD", 200: "#98D8C8", 400: "#F7DC6F", 420: "#FF9FF3"
        }

    def display_stock_info(self, symbol: str, stock) -> None:
        """Display basic stock information."""
        # Always create the placeholder cards first, even if data fetching fails
        self.fundamental_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("💰 Fundamental Analysis", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Divider(height=2),
                    ft.Container(height=300)  # Empty space for analysis content
                ], spacing=10),
                padding=20,
                width=CARD_WIDTH,
                height=CARD_HEIGHT
            ),
            expand=True
        )
        
        self.options_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📈 Options Chain", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Divider(height=2),
                    ft.Container(height=300)  # Empty space for options data
                ], spacing=10),
                padding=20,
                width=CARD_WIDTH,
                height=CARD_HEIGHT
            ),
            expand=True
        )
        
        try:
            # Handle both yfinance Ticker and YahooClient
            info = {}
            
            # Try to get info from stock object
            if hasattr(stock, 'info'):
                if callable(stock.info):
                    # YahooClient has info() method
                    info = stock.info()
                else:
                    # yfinance Ticker has info property
                    info = stock.info
            elif hasattr(stock, '_ticker') and hasattr(stock._ticker, 'info'):
                info = stock._ticker.info
            
            # Ensure info is a dict
            if not isinstance(info, dict):
                print(f"Warning: info is type {type(info)}, converting to dict")
                if hasattr(info, '__dict__'):
                    info = info.__dict__
                else:
                    info = {}
            
            # Create basic info text with safe gets
            info_text = f"""
Symbol: {symbol.upper()}
Name: {info.get('longName', 'N/A')}
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Market Cap: ${info.get('marketCap', 0):,}
P/E Ratio: {info.get('trailingPE', 0):.4f}
52W High: ${info.get('fiftyTwoWeekHigh', 0):.2f}
52W Low: ${info.get('fiftyTwoWeekLow', 0):.2f}
            """.strip()
            
            # Basic information card
            basic_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Basic Information", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                        ft.Divider(height=2),
                        ft.Text(info_text, size=14, color=ft.Colors.GREY_700)
                    ], spacing=10),
                    padding=20,
                    width=CARD_WIDTH,
                    height=CARD_HEIGHT
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
            
        except Exception as e:
            print(f"Error displaying stock info: {e}")
            import traceback
            traceback.print_exc()
            
            # Even on error, create a minimal display
            basic_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Basic Information", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                        ft.Divider(height=2),
                        ft.Text(f"Symbol: {symbol.upper()}\nError loading data", size=14, color=ft.Colors.RED)
                    ], spacing=10),
                    padding=20,
                    width=CARD_WIDTH,
                    height=CARD_HEIGHT
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
        """Display fundamental analysis results in the compact UI."""
        # Check if the fundamental card exists
        if not hasattr(self, 'fundamental_card') or self.fundamental_card is None:
            print("Warning: fundamental_card does not exist yet")
            return
        
        if not self.fundamental_score or not self.fundamental_data:
            return
        
        # Create pillars content (left side)
        pillars_content = []
        # Add overall score as header instead of "Analysis Pillars"
        pillars_content.append(ft.Text(f"Overall Score: {self.fundamental_score['overall_score']} ({self.fundamental_score['score_breakdown']})", 
                                     size=16, weight=ft.FontWeight.BOLD, 
                                     color=ft.Colors.GREEN_600 if self.fundamental_score['overall_score'] == "PASS" else ft.Colors.RED_600))
        pillars_content.append(ft.Divider(height=1))
        
        for pillar_name, pillar_data in self.fundamental_score["pillars"].items():
            status_icon = "✅" if pillar_data["status"] else "❌"
            status_color = ft.Colors.GREEN_700 if pillar_data["status"] else ft.Colors.RED_700
            
            pillar_text = ft.Text(
                f"{status_icon} {pillar_name.replace('_', ' ').title()}: {pillar_data['details']}",
                size=12,
                color=status_color
            )
            pillars_content.append(pillar_text)
        
        # Create metrics content (right side)
        metrics_content = []
        
        # Add specific metrics
        if self.fundamental_data.get('profit_margin') is not None:
            pm = self.fundamental_data['profit_margin']
            pm_status = "✅" if pm >= 0.10 else "❌"
            metrics_content.append(
                ft.Text(f"{pm_status} Profit Margin: {pm:.2%}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
            )
        
        if self.fundamental_data.get('operating_margin') is not None:
            om = self.fundamental_data['operating_margin']
            om_status = "✅" if om >= 0.10 else "❌"
            metrics_content.append(
                ft.Text(f"{om_status} Operating Margin: {om:.2%}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
            )
        
        # Add earnings date if available
        if self.earnings_date:
            metrics_content.append(ft.Text(f"📅 Upcoming Earnings: {self.earnings_date}", size=14, color=ft.Colors.PURPLE_700))
        
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
        """Display options chain analysis in the right column of the three-panel layout."""
        # Check if the options card exists
        if not hasattr(self, 'options_card') or self.options_card is None:
            print("Warning: options_card does not exist yet")
            return
            
        if not self.options_data:
            self.options_card.content.content.controls[1] = ft.Text(
                "Options analysis data not available", 
                size=12, 
                color=ft.Colors.ORANGE
            )
            self.page.update()
            return

        # Build options content
        options_content = []
        current_price = self.options_data.get('current_price', 0)
        strike_range = self.options_data.get('strike_range', 'N/A')
        
        # Add current price and forecast
        if current_price > 0:
            # Use cached forecast data (calculated in chart update)
            forecast_data = self.forecast_data if hasattr(self, 'forecast_data') else None
            
            print(f"Display options - forecast_data: {forecast_data}")
            
            # Check if we have valid forecast data
            has_valid_forecast = False
            if forecast_data:
                pred_price = forecast_data.get('predicted_price')
                if pred_price is not None and not pd.isna(pred_price) and pred_price > 0:
                    has_valid_forecast = True
            
            print(f"Has valid forecast: {has_valid_forecast}")
            
            if has_valid_forecast:
                # Convert numpy types to regular Python types for display
                predicted_price = float(forecast_data['predicted_price'])
                confidence = float(forecast_data.get('confidence', 0))
                trend_slope = float(forecast_data.get('trend_slope', 0))
                price_change_pct = float(forecast_data.get('price_change_pct', 0))
                
                # Compact single row with all forecast metrics
                forecast_details = ft.Row([
                    ft.Text("💰 Current:", size=11, color=ft.Colors.GREY_600),
                    ft.Text(f"${current_price:.2f}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    ft.Container(width=8),
                    ft.Text("🔮 Forecast:", size=11, color=ft.Colors.GREY_600),
                    ft.Text(f"${predicted_price:.2f}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
                    ft.Container(width=8),
                    ft.Text("📈 Change:", size=11, color=ft.Colors.GREY_600),
                    ft.Text(f"{price_change_pct:+.1f}%", 
                           size=14, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.GREEN_600 if price_change_pct > 0 else ft.Colors.RED_600),
                    ft.Container(width=8),
                    ft.Text("✨ Conf:", size=11, color=ft.Colors.GREY_600),
                    ft.Text(f"{confidence:.0f}%", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ft.Container(width=8),
                    ft.Text("📊", size=11),
                    ft.Text("Bullish" if trend_slope > 0 else "Bearish" if trend_slope < 0 else "Neutral",
                           size=14, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.GREEN_600 if trend_slope > 0 else ft.Colors.RED_600 if trend_slope < 0 else ft.Colors.GREY_600)
                ], spacing=3, alignment=ft.MainAxisAlignment.START, tight=True)
                options_content.append(forecast_details)
            else:
                # Show loading indicator instead of N/A
                loading_indicator = ft.Row([
                    ft.Text("🔄 Calculating forecast...", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600, expand=True),
                    ft.ProgressRing(width=20, height=20, stroke_width=2, color=ft.Colors.ORANGE_600)
                ], alignment=ft.MainAxisAlignment.CENTER)
                options_content.append(loading_indicator)
        
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
            
            expiration_date = exp_data.get('expiration', exp_key)
            options = exp_data.get('options', [])
            count = exp_data.get('count', 0)
            
            if count > 0:
                # Create expiration container content
                exp_content = []
                exp_content.append(ft.Text(f"📅 {expiration_date}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700))
                
                # Add table headers (fixed width for better alignment)
                header_row = ft.Row([
                    ft.Text("Strike", size=10, weight=ft.FontWeight.BOLD, width=45),
                    ft.Text("Bid", size=10, weight=ft.FontWeight.BOLD, width=45),
                    ft.Text("Ask", size=10, weight=ft.FontWeight.BOLD, width=45),
                    ft.Text("IV", size=10, weight=ft.FontWeight.BOLD, width=45),
                    ft.Text("OI", size=10, weight=ft.FontWeight.BOLD, width=45),
                    ft.Text("Vol", size=10, weight=ft.FontWeight.BOLD, width=45)
                ], spacing=1, tight=True)
                exp_content.append(header_row)
                
                # Add divider line
                exp_content.append(ft.Container(height=1, bgcolor=ft.Colors.GREY_400))
                
                # Add option rows
                for option in options:
                    strike = option.get('strike', 0)
                    bid = option.get('bid', 0)
                    ask = option.get('ask', 0)
                    iv = option.get('impliedVolatility', 0)
                    open_interest = option.get('openInterest', 0)
                    volume = option.get('volume', 0)
                    strike_color = ft.Colors.GREEN_700 if strike <= current_price else ft.Colors.BLUE_700
                    
                    option_row = ft.Row([
                        ft.Text(f"${strike:.0f}", size=10, weight=ft.FontWeight.BOLD, color=strike_color, width=45),
                        ft.Text(f"${bid:.2f}", size=10, color=ft.Colors.GREY_700, width=45),
                        ft.Text(f"${ask:.2f}", size=10, color=ft.Colors.GREY_700, width=45),
                        ft.Text(f"{iv:.1%}" if iv and iv > 0 else "N/A", size=10, color=ft.Colors.ORANGE_700, width=45),
                        ft.Text(f"{open_interest:,}" if open_interest > 0 else "0", size=10, color=ft.Colors.BLUE_700, width=45),
                        ft.Text(f"{volume:,}" if volume > 0 else "0", size=10, color=ft.Colors.GREEN_700, width=45)
                    ], spacing=1, tight=True)
                    exp_content.append(option_row)
                
                # Create scrollable expiration container (fits within options card)
                expiration_container = ft.Container(
                    content=ft.Column(
                        exp_content, 
                        spacing=2,  # Reduced spacing for more compact layout
                        scroll=ft.ScrollMode.AUTO  # Make it scrollable
                    ),
                    padding=4,  # Reduced padding
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    width=OPTIONS_TABLE_WIDTH,  # Fixed width to fit in container with padding
                    height=OPTIONS_TABLE_HEIGHT,  # Much shorter height to fit in options chain container
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS  # Prevent overflow
                )
                expiration_containers.append(expiration_container)
                
                leaps_found = True
                
                if len(expiration_containers) >= 2:  # Limit to 2 expirations side by side
                    break
        
        # Add expirations side by side with proper sizing
        if expiration_containers:
            expirations_row = ft.Row(
                expiration_containers, 
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,  # Center the containers
                wrap=True  # Allow wrapping if needed
            )
            options_content.append(expirations_row)
        
        if not leaps_found:
            options_content.append(ft.Text("No LEAPS contracts found", size=14, color=ft.Colors.ORANGE))
        
        # Create scrollable column
        options_column = ft.Column(options_content, spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        
        self.options_card.content.content.controls[1] = options_column
        self.page.update()

    def update_chart(self, e=None) -> None:
        """Update the technical analysis chart."""
        print(f"update_chart called for {self.current_symbol}")
        
        if not self.current_symbol:
            return
        
        # Disable update button during loading
        self.update_button.disabled = True
        self.update_button.text = "Updating..."
        self.page.update()
        
        # Start async chart update
        if not self.executor_shutdown:
            try:
                self.executor.submit(self._update_chart_async)
            except RuntimeError:
                # Executor might be shut down, run synchronously as fallback
                self._update_chart_async()
        else:
            # Executor is shut down, run synchronously
            self._update_chart_async()

    def _update_chart_async(self) -> None:
        """Asynchronous chart update."""
        try:
            # Check if controls are initialized
            if not self.timeframe_dropdown:
                print("Chart controls not initialized - skipping chart update")
                return
                
            # Get timeframe
            from ..config.dependencies import YFINANCE_AVAILABLE
            from ..data.yahoo_client import YahooClient
            from ..data.technical_analysis import calculate_indicators, get_base_price
            from ..utils.cache import DataCache
            import yfinance as yf
            from ..utils.exceptions import StockDataError
            
            # Use the global data cache
            from ..config import constants
            
            period = self.timeframe_map[self.timeframe_dropdown.value]
            
            # Check cache first
            df = self.data_cache.get(self.current_symbol, period)
            
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
                self.data_cache.set(self.current_symbol, period, df)
            
            # Prepare data
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.index.name = "Date"
            
            # Calculate indicators
            df_ind = calculate_indicators(df)
            self.current_df = df_ind
            
            # Update UI in main thread - pass period for forecast caching
            self.page.run_thread(lambda: self._on_chart_success(df_ind, period))
            
        except Exception as e:
            error_msg = str(e)
            self.page.run_thread(lambda: self._on_chart_error(error_msg))

    def _on_chart_success(self, df_ind, period: str) -> None:
        """Handle successful chart update."""
        try:
            # Check if Plotly is available
            from ..config.dependencies import PLOTLY_AVAILABLE
            from ..data.technical_analysis import get_base_price, calculate_price_forecast
            import numpy as np
            
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
            mav_list = [period_ma for period_ma, checkbox in self.ma_checkboxes.items() if checkbox.value]
            
            # Get current price for display
            current_price = df_ind["Close"].iloc[-1]
            
            # Calculate and cache the forecast - ALWAYS based on 2 years of data, not current timeframe
            # Only calculate once per symbol, not per timeframe
            forecast_cache_key = f"{self.current_symbol}_forecast"
            
            if not self.forecast_data or not hasattr(self, '_last_forecast_key') or self._last_forecast_key != forecast_cache_key:
                print(f"Calculating price forecast for {self.current_symbol} (always using 2y data)...")
                
                # Fetch 2 years of data specifically for forecast (independent of chart timeframe)
                import yfinance as yf
                forecast_stock = yf.Ticker(self.current_symbol)
                df_2y = forecast_stock.history(period="2y")
                
                if not df_2y.empty:
                    df_2y = df_2y[["Open", "High", "Low", "Close", "Volume"]].copy()
                    df_2y_ind = calculate_indicators(df_2y)
                    self.forecast_data = calculate_price_forecast(df_2y_ind)
                    self._last_forecast_key = forecast_cache_key
                    print(f"Forecast calculated (2y data): {self.forecast_data}")
                else:
                    print("Could not fetch 2y data for forecast, using current timeframe data")
                    self.forecast_data = calculate_price_forecast(df_ind)
                    self._last_forecast_key = forecast_cache_key
            else:
                print(f"Using cached forecast data for {self.current_symbol}")
            
            # Create and display Plotly chart
            print("Creating Plotly chart...")
            try:
                chart_image = self.create_plotly_chart(df_ind)
                print("Chart image created successfully!")
            except Exception as chart_error:
                print(f"ERROR creating chart: {chart_error}")
                import traceback
                traceback.print_exc()
                raise
            
            # Create legend box and display chart with legend
            print("Creating legend box...")
            legend_box = self.create_legend_box(df_ind, base_price)
            print("Legend box created!")
            
            print("Creating chart and legend row...")
            chart_and_legend = ft.Row([
                ft.Container(
                    content=ft.Image(
                        src_base64=chart_image,
                        width=None,  # Allow full width
                        height=800,  # Match the chart height
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
            print("Chart and legend row created!")
            
            print("Updating chart card...")
            self.chart_card.content.content.controls[1] = chart_and_legend
            print("Chart card updated!")
            
            # Show analysis summary
            print("Showing analysis summary...")
            try:
                self.show_analysis_summary(df_ind, current_price, last_rsi, base_price)
                print("Analysis summary shown!")
            except Exception as summary_error:
                print(f"ERROR in show_analysis_summary: {summary_error}")
                import traceback
                traceback.print_exc()
            
            # ALWAYS refresh options display after chart completes (forecast is now ready)
            print(f"Chart complete - current_symbol: {self.current_symbol}, has options_card: {hasattr(self, 'options_card')}, forecast_data: {self.forecast_data is not None}")
            
            if self.current_symbol and hasattr(self, 'options_card') and self.options_card:
                print(f"Refreshing options with calculated forecast for {self.current_symbol}...")
                try:
                    self.display_options_analysis(self.current_symbol)
                    print("Options display refreshed successfully!")
                except Exception as refresh_error:
                    print(f"Error refreshing options: {refresh_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Skipping options refresh - conditions not met")
            
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

    def show_error(self, message: str) -> None:
        """Show an error message to the user."""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def refresh_options_with_forecast(self, ticker: str) -> None:
        """Refresh the options display with updated forecast data."""
        print(f"refresh_options_with_forecast called for {ticker}")
        if hasattr(self, 'options_card') and self.options_card:
            print(f"Forecast data available: {self.forecast_data is not None}")
            self.display_options_analysis(ticker)

    def create_legend_box(self, df_ind, base_price: float) -> ft.Container:
        """Create a separate legend box for the chart with price values."""
        import numpy as np
        
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

    def create_plotly_chart(self, df_ind) -> str:
        """Create a Plotly chart and return base64 encoded image."""
        import numpy as np
        import pandas as pd
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import plotly.io as pio
        import base64
        import time
        from ..data.technical_analysis import get_base_price
        
        # Create cache key based on symbol, timeframe, and MA settings
        mav_list = [period for period, checkbox in self.ma_checkboxes.items() if checkbox.value]
        timeframe = self.timeframe_dropdown.value if self.timeframe_dropdown else "1d"
        cache_key = f"{self.current_symbol}_{timeframe}_{sorted(mav_list)}"
        
        # Check cache first
        current_time = time.time()
        if (cache_key in self.chart_cache and 
            cache_key in self.chart_cache_timestamp and
            current_time - self.chart_cache_timestamp[cache_key] < self.chart_cache_ttl):
            return self.chart_cache[cache_key]
        
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
        
        # Pre-calculate moving averages for better performance
        ma_data_dict = {}
        for ma in mav_list:
            ma_data_dict[ma] = df_ind['Close'].rolling(window=ma, min_periods=1).mean()
        
        # Optimized volume color calculation using vectorized operations
        volume_colors = ['rgba(158,202,225,0.6)']  # Default for first bar
        if len(df_ind) > 1:
            price_changes = df_ind['Close'].diff()
            up_mask = price_changes > 0
            down_mask = price_changes < 0
            
            # Vectorized color assignment
            volume_colors.extend(['rgba(0,255,0,0.6)' if up else 'rgba(255,0,0,0.6)' 
                                for up in up_mask.iloc[1:]])
        
        # Create subplots with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f"{self.current_symbol} - ${current_price:.2f} | RSI: {last_rsi:.1f}" if not np.isnan(last_rsi) else f"{self.current_symbol} - ${current_price:.2f}", ""),
            row_heights=[0.7, 0.3]
        )
        
        # Add candlestick chart with enhanced hover info
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
        
        # Add moving averages with hover info showing MA values
        for ma in mav_list:
            color = self.ma_color_map[ma]
            ma_data = ma_data_dict[ma]
            
            # Create hover template with MA value
            hover_template = f"<b>%{{x}}</b><br>{ma}-day MA: $%{{y:.2f}}<br><extra></extra>"
            
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=ma_data,
                    mode='lines',
                    name=f"{ma}-day MA",
                    line=dict(color=color, width=2),
                    showlegend=True,
                    hovertemplate=hover_template
                ),
                row=1, col=1
            )
        
        # Add support line with hover info
        if "Support" in df_ind and df_ind["Support"].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=df_ind["Support"],
                    mode='lines',
                    name=f"Support (20d): ${last_support:.2f}" if not np.isnan(last_support) else "Support (20d)",
                    line=dict(color="green", dash="dash", width=1.5),
                    showlegend=True,
                    hovertemplate="<b>%{x}</b><br>Support: $%{y:.2f}<br><extra></extra>"
                ),
                row=1, col=1
            )
        
        # Add resistance line with hover info
        if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=df_ind["Resistance"],
                    mode='lines',
                    name=f"Resistance (20d): ${last_resistance:.2f}" if not np.isnan(last_resistance) else "Resistance (20d)",
                    line=dict(color="red", dash="dash", width=1.5),
                    showlegend=True,
                    hovertemplate="<b>%{x}</b><br>Resistance: $%{y:.2f}<br><extra></extra>"
                ),
                row=1, col=1
            )
        
        # Add base price line with hover info
        if not np.isnan(base_price):
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=[base_price] * len(df_ind),
                    mode='lines',
                    name=f"Base Price: ${base_price:.2f}",
                    line=dict(color="orange", dash="dash", width=1.5),
                    showlegend=True,
                    hovertemplate="<b>%{x}</b><br>Base Price: $%{y:.2f}<br><extra></extra>"
                ),
                row=1, col=1
            )
        
        # Add 5% below base price line with hover info
        if below_5p:
            fig.add_trace(
                go.Scatter(
                    x=df_ind.index,
                    y=[below_5p] * len(df_ind),
                    mode='lines',
                    name=f"5% Below Base: ${below_5p:.2f}",
                    line=dict(color="purple", dash="dash", width=1.5),
                    showlegend=True,
                    hovertemplate="<b>%{x}</b><br>5% Below Base: $%{y:.2f}<br><extra></extra>"
                ),
                row=1, col=1
            )
        
        # Add volume chart with optimized colors
        fig.add_trace(
            go.Bar(
                x=df_ind.index,
                y=df_ind['Volume'],
                name="Volume",
                marker_color=volume_colors,
                showlegend=False,
                hovertemplate="<b>%{x}</b><br>Volume: %{y:,.0f}<br><extra></extra>"
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
        
        # Convert chart to image for Flet with optimized settings
        # Increased width for better visibility
        chart_width = 2400  # Much wider for detailed analysis
        chart_height = 800  # Increased height proportionally
        # Scale=1 for faster rendering
        img_bytes = pio.to_image(fig, format="png", width=chart_width, height=chart_height, scale=1)
        chart_image = base64.b64encode(img_bytes).decode()
        
        # Cache the result
        self.chart_cache[cache_key] = chart_image
        self.chart_cache_timestamp[cache_key] = current_time
        
        # Clean up old cache entries
        expired_keys = [key for key, timestamp in self.chart_cache_timestamp.items() 
                       if current_time - timestamp > self.chart_cache_ttl]
        for key in expired_keys:
            self.chart_cache.pop(key, None)
            self.chart_cache_timestamp.pop(key, None)
        
        return chart_image

    def show_analysis_summary(self, df_ind, current_price: float, rsi: float, base_price: float) -> None:
        """Show a summary of the technical and fundamental analysis."""
        import numpy as np
        
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
            summary += f"Overall Score: {self.fundamental_score['overall_score']} ({self.fundamental_score['score_breakdown']})\n"
            
            for pillar_name, pillar_data in self.fundamental_score['pillars'].items():
                status_icon = "✅" if pillar_data['status'] else "❌"
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
                
        # Print to console
        print(summary)
