# Modular Stock Analysis Application

This document describes the new modular structure of the Stock Analysis Application.

## 📁 Project Structure

```
src/
├── config/                 # Configuration and constants
│   ├── __init__.py
│   ├── constants.py       # Analysis thresholds and UI constants
│   └── dependencies.py    # Dependency checking and imports
├── data/                   # Data processing modules
│   ├── __init__.py
│   ├── yahoo_client.py    # Yahoo Finance API client
│   ├── fundamental_analysis.py  # Fundamental analysis functions
│   ├── options_analysis.py     # Options chain analysis
│   └── technical_analysis.py   # Technical indicators and forecasting
├── ui/                     # User interface modules
│   ├── __init__.py
│   └── main_app.py        # Main application class
└── utils/                  # Utility modules
    ├── __init__.py
    ├── exceptions.py      # Custom exceptions
    ├── cache.py          # Data caching utilities
    └── rate_limiter.py   # API rate limiting
main.py                    # Main entry point
run_modular.py            # Simple launcher script
```

## 🚀 Running the Application

### Option 1: Direct execution
```bash
python main.py
```

### Option 2: Using the launcher
```bash
python run_modular.py
```

### Option 3: Original version (if needed)
```bash
python SC_Automated_Analysis.py
```

## 📦 Dependencies

All dependencies are listed in `requirements.txt`. Install them with:
```bash
pip install -r requirements.txt
```

Key dependencies:
- `flet` - GUI framework
- `yfinance` - Financial data
- `pandas`, `numpy` - Data processing
- `plotly` - Charting
- `retry`, `tenacity` - Retry logic
- `requests` - HTTP requests

## 🔧 Development

### Adding New Features

1. **New Analysis Functions**: Add to appropriate module in `src/data/`
2. **New UI Components**: Add to `src/ui/main_app.py` or create new UI modules
3. **New Utilities**: Add to `src/utils/`
4. **Configuration Changes**: Update `src/config/constants.py`

### Module Responsibilities

- **`config/`**: Configuration, constants, and dependency management
- **`data/`**: All data fetching, processing, and analysis logic
- **`ui/`**: User interface and application flow
- **`utils/`**: Reusable utilities and helper functions

## 🐛 Debugging

With the modular structure, you can:
- Debug specific modules independently
- Test individual components
- Easily locate and fix issues
- Add logging to specific modules

## 📈 Benefits

1. **Maintainability**: Easier to understand and modify code
2. **Debugging**: Faster issue identification and resolution
3. **Development**: Parallel development on different modules
4. **Testing**: Test individual components
5. **Reusability**: Use modules in other projects
6. **Documentation**: Clear module-level documentation

## 🔄 Migration from Original

The original `SC_Automated_Analysis.py` (3,635 lines) has been split into:
- **9 focused modules** with clear responsibilities
- **Improved error handling** and dependency management
- **Same functionality** with better organization
- **Enhanced maintainability** for future development

## 📝 Notes

- All original functionality is preserved
- Clean shutdown handling is maintained
- Error handling is improved
- Dependencies are properly managed
- The application runs exactly the same as before
