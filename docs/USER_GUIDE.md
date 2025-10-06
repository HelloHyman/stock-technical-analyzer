# Stock Analyzer - User Guide

Welcome to Stock Analyzer! This guide will help you get the most out of the application.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Understanding Charts](#understanding-charts)
4. [Advanced Features](#advanced-features)
5. [Tips and Tricks](#tips-and-tricks)
6. [FAQ](#faq)

---

## Getting Started

### Installation

**Option 1: Using the Executable (Easiest)**
1. Download `StockAnalyzer.exe`
2. Double-click to run
3. If you see a Windows SmartScreen warning:
   - Click "More info"
   - Click "Run anyway"

**Option 2: Running from Python**
1. Install Python 3.8+ from https://www.python.org/
2. Open Command Prompt or PowerShell
3. Install dependencies:
   ```
   pip install pandas numpy yfinance matplotlib mplfinance
   ```
4. Run the application:
   ```
   python manual_stock_analyzer.py
   ```

### First Launch

When you first open Stock Analyzer, you'll see:
- **Symbol Input Field**: Enter stock or crypto symbols here
- **Chart Controls**: Customize your view
- **Chart Area**: Where your analysis appears

---

## Basic Usage

### Step 1: Enter a Symbol

In the symbol input field, type:
- **Stocks**: `AAPL`, `MSFT`, `GOOGL`, `TSLA`, etc.
- **Crypto**: `BTC-USD`, `ETH-USD`, `ADA-USD`, etc.
- **Indices**: `^GSPC`, `^DJI`, `^IXIC`, etc.

**Tip**: Press `Enter` after typing to analyze immediately!

### Step 2: Analyze

Click the **"Analyze"** button or press `Enter`.

The app will:
1. Fetch historical data from Yahoo Finance
2. Calculate technical indicators
3. Display an interactive chart
4. Show symbol information

### Step 3: Customize

Use the **Chart Controls** to:
- **Change Timeframe**: Select from 1 day to Max history
- **Toggle Moving Averages**: Check/uncheck MAs you want to see
- **Update Chart**: Click to apply your changes

---

## Understanding Charts

### Chart Components

#### 1. Candlesticks
- **Green Candle**: Price went up (Close > Open)
- **Red Candle**: Price went down (Close < Open)
- **Wicks**: Show high and low prices

#### 2. Moving Averages (MAs)
Colored lines showing average prices over time:
- **10 MA** (Red): Short-term trend
- **20 MA** (Cyan): Medium-short trend
- **50 MA** (Green): Medium-term trend
- **200 MA** (Light Green): Long-term trend
- **400 MA** (Yellow): Very long-term trend

**How to use MAs:**
- Price above MA = Uptrend
- Price below MA = Downtrend
- MA crossovers = Potential trend change

#### 3. Support and Resistance
- **🟢 Green Dashed Line**: Support (20-day low)
  - Price tends to bounce up from this level
  - Potential buying opportunity near support

- **🔴 Red Dashed Line**: Resistance (20-day high)
  - Price tends to bounce down from this level
  - Potential selling opportunity near resistance

#### 4. Base Price
- **🟠 Orange Dashed Line**: Calculated entry point
  - Average of support levels and RSI oversold points
  - Suggests a reasonable buying price

- **🟣 Purple Dashed Line**: 5% below base
  - Even more conservative entry point

#### 5. RSI (Relative Strength Index)
Shown in the chart title:
- **RSI > 70**: Overbought (⚠️ might drop soon)
- **RSI < 30**: Oversold (✅ might rise soon)
- **RSI 30-70**: Neutral

#### 6. Volume
Bottom panel shows trading volume:
- High volume = Strong interest
- Low volume = Weak interest
- Volume spikes often precede price moves

---

## Advanced Features

### Timeframe Selection

Choose different timeframes to analyze:

| Timeframe | Best For |
|-----------|----------|
| 1 Day | Intraday trading |
| 5 Days | Very short-term |
| 1 Month | Day trading |
| 3 Months | Swing trading |
| 6 Months | Short-term investing |
| 1 Year | Medium-term trends |
| 2 Years | Long-term analysis |
| 5 Years | Major trend patterns |
| 10 Years | Historical perspective |
| Max | Complete history |

### Moving Average Combinations

**Popular combinations:**

1. **Day Trading**: 10, 20, 50 MA
   - Quick signals for short-term trades

2. **Swing Trading**: 20, 50, 200 MA
   - Medium-term trend identification

3. **Long-term Investing**: 50, 200, 400 MA
   - Major trend changes

4. **Full Analysis**: All MAs
   - Complete picture (can be crowded)

### Reading the Symbol Information

The info panel shows:
- **Name**: Company or asset name
- **Sector/Industry**: For stocks
- **Market Cap**: Company/asset size
- **52W High/Low**: Yearly range
- **P/E Ratio**: Valuation metric (stocks only)

---

## Tips and Tricks

### Finding Good Entry Points

1. **Look for:**
   - Price near support level (green line)
   - RSI below 30 (oversold)
   - Price near or below base price (orange line)

2. **Confirm with:**
   - Price above 200 MA (long-term uptrend)
   - Volume increase
   - Bullish candlestick patterns

### Identifying Trends

**Uptrend signals:**
- Price consistently above 50 and 200 MA
- MAs sloping upward
- Higher highs and higher lows

**Downtrend signals:**
- Price consistently below 50 and 200 MA
- MAs sloping downward
- Lower highs and lower lows

### Using Multiple Timeframes

**Multi-timeframe analysis:**
1. Start with long timeframe (1-2 years)
   - Identify major trend
2. Medium timeframe (3-6 months)
   - Find current trend phase
3. Short timeframe (1 month)
   - Pinpoint entry/exit points

### Keyboard Shortcuts

- **Enter**: Analyze current symbol
- **Tab**: Navigate between fields
- **Spacebar**: Toggle checkboxes

---

## Common Patterns to Watch

### 1. Golden Cross
- 50 MA crosses above 200 MA
- Bullish signal

### 2. Death Cross
- 50 MA crosses below 200 MA
- Bearish signal

### 3. Support Bounce
- Price touches support and rebounds
- Buying opportunity

### 4. Resistance Breakout
- Price breaks above resistance
- Potential strong upward move

### 5. RSI Divergence
- Price makes new low, RSI doesn't
- Potential reversal

---

## Example Analysis Workflow

Let's analyze Apple (AAPL):

1. **Enter Symbol**: `AAPL`
2. **Analyze**: View 2-year chart
3. **Check Trend**: Is price above 200 MA?
4. **Find Support**: Note the green support line
5. **Check RSI**: Is it neutral (30-70)?
6. **Adjust Timeframe**: Try 6 months for detail
7. **Add MAs**: Enable 50, 200 MA
8. **Look for Entry**: Price near support + RSI low?
9. **Make Decision**: Based on all indicators

---

## FAQ

### Q: Why can't I find my stock?
**A:** 
- Check spelling
- Some stocks have different ticker symbols
- Small/foreign stocks may not be in Yahoo Finance
- Try adding the exchange (e.g., `TICKER.L` for London)

### Q: Why is data missing for old dates?
**A:** 
- Newer companies have limited history
- Some symbols were renamed
- Data may not be available in Yahoo Finance

### Q: What's the difference between stocks and crypto symbols?
**A:** 
- Stocks: Just the ticker (e.g., `AAPL`)
- Crypto: Add `-USD` (e.g., `BTC-USD`)

### Q: Can I analyze forex?
**A:** 
- Yes! Use format like `EURUSD=X`
- Common pairs: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`

### Q: How often does data update?
**A:** 
- Real-time for current price
- Historical data cached for 5 minutes
- Re-analyze to refresh data

### Q: Can I export the chart?
**A:** 
- Currently not supported in the app
- Use Windows Snipping Tool or Print Screen

### Q: Is this investment advice?
**A:** 
- **No!** This is a technical analysis tool
- Always do your own research
- Consult financial professionals
- Past performance ≠ future results

### Q: Why do I see a SmartScreen warning?
**A:** 
- This is normal for new executables
- Click "More info" → "Run anyway"
- The app is safe to run
- Warnings disappear as the app builds reputation

### Q: Can I use this offline?
**A:** 
- No, internet connection required
- Data is fetched from Yahoo Finance
- Charts won't work without connection

---

## Troubleshooting

### Problem: "No data found"
**Solution:**
- Check symbol spelling
- Try a different timeframe
- Verify internet connection

### Problem: Chart is too crowded
**Solution:**
- Disable some moving averages
- Use fewer MAs (2-3 recommended)
- Zoom in on specific date range

### Problem: Application is slow
**Solution:**
- Reduce number of MAs
- Use shorter timeframes
- Clear cache by restarting app
- Check internet speed

### Problem: Can't see some indicators
**Solution:**
- Maximize window for better view
- Resize window if needed
- Some indicators may be off-screen

---

## Best Practices

### ✅ DO:
- Analyze multiple timeframes
- Combine indicators for confirmation
- Use support/resistance with RSI
- Paper trade before real trading
- Keep learning about technical analysis

### ❌ DON'T:
- Rely on single indicator
- Ignore the overall trend
- Trade based solely on this app
- Risk money you can't afford to lose
- Ignore fundamental analysis

---

## Additional Resources

**Learn Technical Analysis:**
- Investopedia: https://www.investopedia.com/
- TradingView Education: https://www.tradingview.com/education/
- Books: "Technical Analysis of the Financial Markets" by John Murphy

**Practice Trading:**
- Paper trading accounts
- Stock market simulators
- Demo trading platforms

**Stay Informed:**
- Financial news websites
- Company earnings reports
- Economic calendars
- Market analysis blogs

---

## Support

**Need help?**
- Re-read this guide
- Check README.md for technical issues
- Review SIGNING_GUIDE.md for .exe issues

**Found a bug?**
- Note the error message
- Check what you were doing
- Try restarting the application

---

## Safety Reminder

⚠️ **Important:**
- This tool is for analysis only
- Not financial advice
- Do your own research
- Consult professionals
- Trade responsibly
- Only risk what you can afford to lose

---

## Quick Reference Card

```
📊 QUICK REFERENCE

SYMBOLS:
Stocks: AAPL, MSFT, GOOGL
Crypto: BTC-USD, ETH-USD
Index: ^GSPC, ^DJI

INDICATORS:
🟢 Support     - Buy zone
🔴 Resistance  - Sell zone
🟠 Base Price  - Entry point
🟣 5% Below    - Safe entry
📊 RSI <30     - Oversold
📊 RSI >70     - Overbought

MAs:
10/20/30 - Short term
50 - Medium term
200 - Long term
400 - Very long term

TIPS:
✅ Price near support
✅ RSI below 30
✅ Above 200 MA
✅ Volume increase
❌ RSI above 70
❌ Below support
```

---

**Happy Trading! 📈**

Remember: Smart trading is patient trading. Take your time, do your research, and never invest more than you can afford to lose.

