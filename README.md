# 📈 Stock Analyzer - Web Dashboard

**Live interactive stock and cryptocurrency technical analysis dashboard built with Dash & Plotly**

![Python](https://img.shields.io/badge/python-3.11-blue)
![Dash](https://img.shields.io/badge/dash-2.14-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Live Demo

**[View Live Dashboard](#)** *(Deploy first)*

## ✨ Features

- 📊 **Real-time stock & crypto data** from Yahoo Finance
- 📈 **Interactive candlestick charts** with Plotly
- 🎯 **Technical indicators:**
  - RSI (Relative Strength Index)
  - Support & Resistance levels (20-day)
  - Base price calculation
  - Moving Averages (20, 50, 100, 200-day)
- 📅 **Multiple timeframes** (1 day to 5 years)
- 🎨 **Modern, responsive UI** with Bootstrap
- 🔄 **Live updates** and interactive controls
- 📱 **Mobile-friendly** design

## 🖥️ Screenshots

*Add screenshots here after deployment*

## 🛠️ Tech Stack

- **Frontend:** Dash, Plotly, Bootstrap
- **Backend:** Python, Flask (via Dash)
- **Data:** yfinance (Yahoo Finance API)
- **Analysis:** pandas, numpy
- **Deployment:** Heroku / Render / Railway

## 🚀 Quick Start

### Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer.git
   cd Automated-Stock-and-Crypto-Analyzer
   git checkout feature/dash-web-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   ```
   http://localhost:8050
   ```

## 📤 Deployment

### Deploy to Render (Recommended - Free Tier)

1. **Create account:** https://render.com

2. **New Web Service:**
   - Connect your GitHub repo
   - Branch: `feature/dash-web-dashboard`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server`

3. **Deploy!**

### Deploy to Heroku

1. **Install Heroku CLI:** https://devcenter.heroku.com/articles/heroku-cli

2. **Create app:**
   ```bash
   heroku create stock-analyzer-dashboard
   ```

3. **Deploy:**
   ```bash
   git push heroku feature/dash-web-dashboard:main
   ```

4. **Open:**
   ```bash
   heroku open
   ```

### Deploy to Railway

1. **Create account:** https://railway.app

2. **New Project:**
   - Connect GitHub repo
   - Select branch: `feature/dash-web-dashboard`
   - Auto-detects Python app

3. **Deploy automatically**

## 📊 Usage

### Analyze a Stock

1. **Enter symbol** (e.g., AAPL, MSFT, TSLA)
2. **Select timeframe** (1 day to 5 years)
3. **Choose moving averages** to display
4. **Click "Analyze"**

### Symbols Supported

**Stocks:**
- `AAPL` - Apple
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla
- `NVDA` - NVIDIA

**Crypto:**
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `ADA-USD` - Cardano
- `SOL-USD` - Solana

**Indices:**
- `^GSPC` - S&P 500
- `^DJI` - Dow Jones
- `^IXIC` - NASDAQ

## 🎨 Chart Indicators

- **🟢 Green line:** Support level (20-day low)
- **🔴 Red line:** Resistance level (20-day high)
- **🟠 Orange line:** Base price (suggested entry point)
- **📊 RSI:** >70 = Overbought, <30 = Oversold
- **📈 Moving Averages:** Trend indicators

## 🔧 Configuration

### Environment Variables

No environment variables needed! Uses public Yahoo Finance API.

### Custom Port

```bash
# Default port 8050
python app.py

# Custom port
PORT=5000 python app.py
```

## 📝 Project Structure

```
Stock-Analyzer/
├── app.py                 # Main Dash application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku/Render deployment
├── runtime.txt           # Python version
├── LICENSE               # MIT License
├── README.md             # This file
└── .gitignore           # Git ignore patterns
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

Licensed under the [MIT License](LICENSE).

## ⚠️ Disclaimer

**Important:** This tool is for educational and informational purposes only. It is not financial advice, investment advice, or trading advice. Always do your own research and consult with licensed financial professionals before making any investment decisions.

Stock data provided by Yahoo Finance.

## 🌟 Acknowledgments

- **yfinance** - Yahoo Finance API wrapper
- **Plotly** - Interactive visualization library
- **Dash** - Python web framework
- **Bootstrap** - UI components

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/discussions)

---

**Made with ❤️ for traders and investors**

⭐ Star this repo if you find it useful!
