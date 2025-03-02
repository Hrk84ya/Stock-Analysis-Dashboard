import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def get_stock_data(symbol, period='1y'):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        return None, None

def create_comparison_chart(stocks_data):
    """Create a comparison chart for multiple stocks"""
    fig = go.Figure()

    # Normalize all prices to percentage change from first day
    for symbol, df in stocks_data.items():
        initial_price = df['Close'].iloc[0]
        normalized_prices = ((df['Close'] - initial_price) / initial_price) * 100

        fig.add_trace(go.Scatter(
            x=df.index,
            y=normalized_prices,
            name=symbol,
            mode='lines',
            hovertemplate=
            f"{symbol}<br>" +
            "Date: %{x}<br>" +
            "Change: %{y:.2f}%<br>"
        ))

    fig.update_layout(
        title='Percentage Change Comparison',
        yaxis_title='Percentage Change (%)',
        template='plotly_dark',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def identify_candlestick_patterns(df):
    """Identify basic candlestick patterns"""
    patterns = []

    # Calculate body and shadows
    df['Body'] = df['Close'] - df['Open']
    df['Upper_Shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['Lower_Shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']

    for i in range(len(df)):
        if i < 2:  # Skip first two rows as they need previous data
            continue

        # Doji
        if abs(df['Body'].iloc[i]) <= 0.1 * df['Close'].iloc[i]:
            patterns.append(('Doji', i))

        # Hammer
        elif (df['Lower_Shadow'].iloc[i] > 2 * abs(df['Body'].iloc[i]) and
              df['Upper_Shadow'].iloc[i] <= abs(df['Body'].iloc[i])):
            patterns.append(('Hammer', i))

        # Shooting Star
        elif (df['Upper_Shadow'].iloc[i] > 2 * abs(df['Body'].iloc[i]) and
              df['Lower_Shadow'].iloc[i] <= abs(df['Body'].iloc[i])):
            patterns.append(('Shooting Star', i))

        # Engulfing
        elif (df['Body'].iloc[i-1] < 0 and df['Body'].iloc[i] > 0 and
              abs(df['Body'].iloc[i]) > abs(df['Body'].iloc[i-1])):
            patterns.append(('Bullish Engulfing', i))
        elif (df['Body'].iloc[i-1] > 0 and df['Body'].iloc[i] < 0 and
              abs(df['Body'].iloc[i]) > abs(df['Body'].iloc[i-1])):
            patterns.append(('Bearish Engulfing', i))

    return patterns

def create_price_chart(df):
    """Create an interactive price chart using Plotly"""
    fig = go.Figure()

    # Main candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ))

    # Volume bars
    colors = ['red' if row['Open'] > row['Close'] else 'green' for i, row in df.iterrows()]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color=colors,
        yaxis='y2'
    ))

    # Add candlestick patterns
    patterns = identify_candlestick_patterns(df)
    for pattern_name, idx in patterns:
        fig.add_annotation(
            x=df.index[idx],
            y=df['High'].iloc[idx],
            text=pattern_name,
            showarrow=True,
            arrowhead=1
        )

    fig.update_layout(
        title='Stock Price History with Patterns',
        yaxis_title='Price',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right'
        ),
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig

def format_large_number(number):
    """Format large numbers to human-readable format"""
    if number is None:
        return "N/A"

    billion = 1_000_000_000
    million = 1_000_000

    if number >= billion:
        return f"${number/billion:.2f}B"
    elif number >= million:
        return f"${number/million:.2f}M"
    else:
        return f"${number:,.2f}"

def get_key_metrics(info):
    """Extract and format key metrics from stock info"""
    metrics = {
        'Market Cap': format_large_number(info.get('marketCap')),
        'P/E Ratio': f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else 'N/A',
        'EPS': f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') else 'N/A',
        'Revenue': format_large_number(info.get('totalRevenue')),
        '52 Week High': f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
        '52 Week Low': f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A',
        'Volume': f"{info.get('volume', 'N/A'):,}" if info.get('volume') else 'N/A',
        'Dividend Yield': f"{info.get('dividendYield', 'N/A')*100:.2f}%" if info.get('dividendYield') else 'N/A',
    }
    return metrics