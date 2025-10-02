#!/usr/bin/env python3
"""
Manual Stock Technical Analyzer
- Enter any stock symbol manually for technical analysis
- Interactive chart with moving averages and indicators
- Support/Resistance levels and RSI analysis
- Customizable timeframes and chart settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
from typing import List, Optional

# -----------------------------------------------------------------------------
# TECHNICAL INDICATORS
# -----------------------------------------------------------------------------
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Support/Resistance (20d) and RSI."""
    if df.empty:
        return df
    df = df.copy()
    df["Support"] = df["Low"].rolling(window=20).min()
    df["Resistance"] = df["High"].rolling(window=20).max()

    # RSI Calculation
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    
    return df

def get_base_price(df: pd.DataFrame) -> float:
    """Calculate base price using support levels and RSI oversold conditions."""
    recent = df.tail(20)
    if recent.empty:
        return float("nan")

    avg_support = recent["Support"].mean()
    min_low = recent["Low"].min()
    oversold = recent[recent["RSI"] < 30]
    rsi_buy = oversold["Close"].min() if not oversold.empty else np.nan

    possibilities = [avg_support, min_low, rsi_buy]
    possibilities = [p for p in possibilities if not np.isnan(p)]
    if not possibilities:
        return float("nan")
    return round(float(np.mean(possibilities)), 2)

# -----------------------------------------------------------------------------
# MAIN APPLICATION CLASS
# -----------------------------------------------------------------------------
class ManualStockAnalyzer:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface."""
        self.root.title("Manual Stock Technical Analyzer")
        self.root.geometry("900x800")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Stock input section
        input_frame = ttk.LabelFrame(main_frame, text="Stock Symbol Input", padding=10)
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="Enter Stock Symbol:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        input_control_frame = ttk.Frame(input_frame)
        input_control_frame.pack(fill="x", pady=5)
        
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(input_control_frame, textvariable=self.symbol_var, font=("Segoe UI", 12))
        self.symbol_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.symbol_entry.bind('<Return>', lambda e: self.analyze_stock())
        
        self.analyze_button = ttk.Button(input_control_frame, text="Analyze Stock", command=self.analyze_stock)
        self.analyze_button.pack(side="right")
        
        # Chart controls section
        controls_frame = ttk.LabelFrame(main_frame, text="Chart Controls", padding=10)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Timeframe selection
        timeframe_frame = ttk.Frame(controls_frame)
        timeframe_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(timeframe_frame, text="Timeframe:").pack(side="left", padx=(0, 10))
        self.timeframe_var = tk.StringVar(value="2y")
        self.timeframe_map = {
            "1 day": "1d",
            "5 days": "5d", 
            "1 month": "1mo",
            "3 months": "3mo",
            "6 months": "6mo",
            "1 year": "1y",
            "2 years": "2y",
            "5 years": "5y",
            "10 years": "10y",
            "Max": "max"
        }
        
        self.timeframe_cb = ttk.Combobox(
            timeframe_frame,
            textvariable=self.timeframe_var,
            values=list(self.timeframe_map.keys()),
            state="readonly",
            width=10
        )
        self.timeframe_cb.pack(side="left", padx=(0, 20))
        self.timeframe_cb.set("2 years")
        
        # Moving averages checkboxes
        ma_frame = ttk.Frame(controls_frame)
        ma_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(ma_frame, text="Moving Averages:").pack(side="left", padx=(0, 10))
        
        self.ma_vars = {}
        ma_periods = [10, 20, 30, 50, 72, 100, 200, 400]
        for i, period in enumerate(ma_periods):
            var = tk.BooleanVar(value=(period in [50, 200]))  # Default to 50 and 200 MA
            self.ma_vars[period] = var
            cb = ttk.Checkbutton(ma_frame, text=f"{period} MA", variable=var)
            cb.pack(side="left", padx=(0, 5))
        
        # Update button
        update_frame = ttk.Frame(controls_frame)
        update_frame.pack(fill="x")
        
        self.update_button = ttk.Button(update_frame, text="Update Chart", command=self.update_chart)
        self.update_button.pack(side="left")
        
        # Stock info frame
        self.info_frame = ttk.LabelFrame(main_frame, text="Stock Information", padding=10)
        self.info_frame.pack(fill="x", pady=(0, 10))
        
        # Chart frame
        self.chart_frame = ttk.Frame(main_frame)
        self.chart_frame.pack(fill="both", expand=True)
        
        self.canvas = None
        self.current_symbol = None
        self.current_df = None
        
        # MA color mapping
        self.ma_color_map = {
            10: "C0", 20: "C1", 30: "C2", 50: "C3", 
            72: "C4", 100: "C5", 200: "C6", 400: "C7"
        }
        
    def display_stock_info(self, ticker, stock_info):
        """Display basic stock information."""
        # Clear existing info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        info_text = f"Symbol: {ticker.upper()}\n"
        
        if hasattr(stock_info, 'info') and stock_info.info:
            info = stock_info.info
            info_text += f"Company: {info.get('longName', 'N/A')}\n"
            info_text += f"Sector: {info.get('sector', 'N/A')}\n"
            info_text += f"Industry: {info.get('industry', 'N/A')}\n"
            info_text += f"Market Cap: ${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "Market Cap: N/A\n"
            info_text += f"P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
            info_text += f"52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            info_text += f"52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
        else:
            info_text += "Company: Information not available\n"
            
        ttk.Label(self.info_frame, text=info_text, font=("Courier New", 9), justify="left").pack(anchor="w")
        
    def analyze_stock(self):
        """Main function to analyze the entered stock symbol."""
        symbol = self.symbol_var.get().strip().upper()
        
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a stock symbol.")
            return
            
        try:
            # Validate symbol by trying to get stock info
            stock = yf.Ticker(symbol)
            stock_info = stock.info
            
            # Test if we can get price data
            test_data = stock.history(period="5d")
            if test_data.empty:
                messagebox.showerror("No Data", f"No price data found for symbol: {symbol}")
                return
                
            self.current_symbol = symbol
            self.display_stock_info(symbol, stock)
            self.update_chart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing {symbol}: {str(e)}")
            
    def update_chart(self):
        """Update the chart with current settings."""
        if not self.current_symbol:
            messagebox.showwarning("No Symbol", "Please enter and analyze a stock symbol first.")
            return
            
        try:
            # Clear existing chart
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
                
            # Get timeframe
            period = self.timeframe_map[self.timeframe_var.get()]
            
            # Fetch data
            stock = yf.Ticker(self.current_symbol)
            df = stock.history(period=period)
            
            if df.empty:
                messagebox.showwarning("No Data", f"No data for {self.current_symbol} in '{period}' timeframe.")
                return
                
            # Prepare data
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.index.name = "Date"
            
            # Calculate indicators
            df_ind = calculate_indicators(df)
            self.current_df = df_ind
            
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
                addplots.append(mpf.make_addplot(df_ind["Support"], color="green", linestyle="--", width=1))
            if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
                addplots.append(mpf.make_addplot(df_ind["Resistance"], color="red", linestyle="--", width=1))
            if not np.isnan(base_price):
                addplots.append(mpf.make_addplot([base_price] * len(df_ind), color="orange", linestyle="--", width=1))
            if below_5p:
                addplots.append(mpf.make_addplot([below_5p] * len(df_ind), color="purple", linestyle="--", width=1))
                
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
                figsize=(12, 8)
            )
            
            # Add legend
            main_ax = axlist[0]
            legend_handles = []
            legend_labels = []
            
            # Add MA legends
            for ma in mav_list:
                color = self.ma_color_map[ma]
                legend_handles.append(Line2D([], [], color=color, label=f"{ma}-day MA"))
                legend_labels.append(f"{ma}-day MA")
                
            # Add indicator legends
            if "Support" in df_ind and df_ind["Support"].notna().any():
                sup_label = f"Support (20d): ${last_support:.2f}" if not np.isnan(last_support) else "Support (20d)"
                legend_handles.append(Line2D([], [], color="green", linestyle="--", label=sup_label))
                legend_labels.append(sup_label)
                
            if "Resistance" in df_ind and df_ind["Resistance"].notna().any():
                res_label = f"Resistance (20d): ${last_resistance:.2f}" if not np.isnan(last_resistance) else "Resistance (20d)"
                legend_handles.append(Line2D([], [], color="red", linestyle="--", label=res_label))
                legend_labels.append(res_label)
                
            if not np.isnan(base_price):
                bp_label = f"Base Price: ${base_price:.2f}"
                legend_handles.append(Line2D([], [], color="orange", linestyle="--", label=bp_label))
                legend_labels.append(bp_label)
                
            if below_5p:
                b5_label = f"5% Below Base: ${below_5p:.2f}"
                legend_handles.append(Line2D([], [], color="purple", linestyle="--", label=b5_label))
                legend_labels.append(b5_label)
                
            # Add RSI info to title
            current_price = df_ind["Close"].iloc[-1]
            title_text = f"{self.current_symbol} - Current: ${current_price:.2f}"
            if not np.isnan(last_rsi):
                title_text += f" | RSI: {last_rsi:.1f}"
            main_ax.set_title(title_text, fontsize=12, fontweight='bold')
            
            if legend_handles:
                main_ax.legend(legend_handles, legend_labels, loc="best", fontsize=8)
                
            # Display chart
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Show analysis summary
            self.show_analysis_summary(df_ind, current_price, last_rsi, base_price)
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error updating chart: {str(e)}")
            
    def show_analysis_summary(self, df_ind, current_price, rsi, base_price):
        """Show a summary of the technical analysis."""
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
                
        # Show in a message box (you could also add this to a dedicated summary frame)
        print(summary)  # For now, just print to console

# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = ManualStockAnalyzer(root)
    
    # Set focus to symbol entry
    app.symbol_entry.focus()
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()

