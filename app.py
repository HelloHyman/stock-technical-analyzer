"""
Stock Analyzer - Dash Web Dashboard
Interactive stock and crypto technical analysis dashboard
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # For deployment

# ==================== TECHNICAL INDICATORS ====================

def calculate_indicators(df):
    """Calculate technical indicators"""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Support/Resistance
    df['Support'] = df['Low'].rolling(window=20, min_periods=1).min()
    df['Resistance'] = df['High'].rolling(window=20, min_periods=1).max()
    
    # RSI
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
    except:
        df['RSI'] = np.nan
    
    return df

def get_base_price(df):
    """Calculate base price for entry point"""
    if df.empty or len(df) < 20:
        return np.nan
    
    try:
        recent = df.tail(20)
        avg_support = recent['Support'].mean() if 'Support' in recent else np.nan
        min_low = recent['Low'].min()
        
        rsi_buy = np.nan
        if 'RSI' in recent:
            oversold = recent[recent['RSI'] < 30]
            if not oversold.empty:
                rsi_buy = oversold['Close'].min()
        
        possibilities = [p for p in [avg_support, min_low, rsi_buy] if not np.isnan(p)]
        return round(float(np.mean(possibilities)), 2) if possibilities else np.nan
    except:
        return np.nan

# ==================== LAYOUT ====================

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📈 Stock Analyzer Dashboard", className="text-center mb-4 mt-4"),
            html.P("Real-time stock and cryptocurrency technical analysis", className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Enter Symbol", className="card-title"),
                    dbc.InputGroup([
                        dbc.Input(
                            id='symbol-input',
                            type='text',
                            placeholder='e.g., AAPL, BTC-USD, TSLA',
                            value='AAPL'
                        ),
                        dbc.Button("Analyze", id='analyze-button', color='primary')
                    ]),
                    html.Small("Stocks: AAPL, MSFT, GOOGL | Crypto: BTC-USD, ETH-USD", className="text-muted")
                ])
            ], className="mb-3")
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Timeframe", className="card-title"),
                    dcc.Dropdown(
                        id='timeframe-dropdown',
                        options=[
                            {'label': '1 Day', 'value': '1d'},
                            {'label': '5 Days', 'value': '5d'},
                            {'label': '1 Month', 'value': '1mo'},
                            {'label': '3 Months', 'value': '3mo'},
                            {'label': '6 Months', 'value': '6mo'},
                            {'label': '1 Year', 'value': '1y'},
                            {'label': '2 Years', 'value': '2y'},
                            {'label': '5 Years', 'value': '5y'},
                        ],
                        value='6mo'
                    )
                ])
            ], className="mb-3")
        ], md=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Moving Averages", className="card-title"),
                    dbc.Checklist(
                        id='ma-checklist',
                        options=[
                            {'label': ' 20 MA', 'value': 20},
                            {'label': ' 50 MA', 'value': 50},
                            {'label': ' 100 MA', 'value': 100},
                            {'label': ' 200 MA', 'value': 200},
                        ],
                        value=[50, 200],
                        inline=True,
                        switch=True
                    )
                ])
            ], className="mb-3")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='stock-info', className="mb-3")
                ])
            ])
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(id='stock-chart', style={'height': '600px'})
                ]
            )
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='analysis-summary', className="mt-3")
        ])
    ]),
    
    html.Hr(),
    html.Footer([
        html.P("⚠️ Disclaimer: This tool is for educational purposes only. Not financial advice.", 
               className="text-center text-muted")
    ])
    
], fluid=True)

# ==================== CALLBACKS ====================

@app.callback(
    [Output('stock-chart', 'figure'),
     Output('stock-info', 'children'),
     Output('analysis-summary', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('symbol-input', 'value'),
     State('timeframe-dropdown', 'value'),
     State('ma-checklist', 'value')]
)
def update_chart(n_clicks, symbol, timeframe, ma_values):
    if not symbol:
        return go.Figure(), "Enter a symbol to begin", ""
    
    try:
        # Fetch data
        stock = yf.Ticker(symbol.upper())
        df = stock.history(period=timeframe)
        
        if df.empty:
            return go.Figure(), f"No data found for {symbol}", ""
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Get stock info
        info = stock.info
        name = info.get('longName', info.get('shortName', symbol.upper()))
        current_price = df['Close'].iloc[-1]
        
        # Stock info card
        stock_info_content = dbc.Alert([
            html.H4(f"{name} ({symbol.upper()})", className="alert-heading"),
            html.Hr(),
            html.P([
                html.Strong("Current Price: "), f"${current_price:.2f}",
                html.Br(),
                html.Strong("Market Cap: "), f"${info.get('marketCap', 0):,}" if info.get('marketCap') else "N/A"
            ])
        ], color="info")
        
        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{symbol.upper()} Price Chart', 'Volume')
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Moving averages
        ma_colors = {20: '#FF6B6B', 50: '#4ECDC4', 100: '#45B7D1', 200: '#96CEB4'}
        for ma in ma_values:
            if len(df) >= ma:
                df[f'MA{ma}'] = df['Close'].rolling(window=ma).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[f'MA{ma}'],
                        name=f'{ma} MA',
                        line=dict(color=ma_colors.get(ma, '#888888'), width=2)
                    ),
                    row=1, col=1
                )
        
        # Support/Resistance
        if 'Support' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Support'],
                    name='Support',
                    line=dict(color='green', dash='dash', width=1.5)
                ),
                row=1, col=1
            )
        
        if 'Resistance' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Resistance'],
                    name='Resistance',
                    line=dict(color='red', dash='dash', width=1.5)
                ),
                row=1, col=1
            )
        
        # Base price
        base_price = get_base_price(df)
        if not np.isnan(base_price):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[base_price] * len(df),
                    name='Base Price',
                    line=dict(color='orange', dash='dash', width=1.5)
                ),
                row=1, col=1
            )
        
        # Volume
        colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f'{symbol.upper()} Technical Analysis',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            height=600,
            template='plotly_white'
        )
        
        # Analysis summary
        last_rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else np.nan
        
        summary_content = dbc.Alert([
            html.H5("📊 Technical Analysis Summary", className="alert-heading"),
            html.Hr(),
            html.P([
                html.Strong("Current Price: "), f"${current_price:.2f}",
                html.Br(),
                html.Strong("RSI: "), 
                f"{last_rsi:.1f}" if not np.isnan(last_rsi) else "N/A",
                " (Overbought ⚠️)" if last_rsi > 70 else " (Oversold ✅)" if last_rsi < 30 else " (Neutral)" if not np.isnan(last_rsi) else "",
                html.Br(),
                html.Strong("Base Price: "), 
                f"${base_price:.2f}" if not np.isnan(base_price) else "N/A",
                f" (Below Base - Potential Buy ✅)" if not np.isnan(base_price) and current_price <= base_price else ""
            ])
        ], color="success" if (not np.isnan(last_rsi) and last_rsi < 30) or (not np.isnan(base_price) and current_price <= base_price) else "warning")
        
        return fig, stock_info_content, summary_content
        
    except Exception as e:
        error_msg = dbc.Alert(f"Error: {str(e)}", color="danger")
        return go.Figure(), error_msg, ""

# ==================== RUN ====================

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

