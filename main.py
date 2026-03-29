import streamlit as st
import pandas as pd
from utils import get_stock_data, create_price_chart, get_key_metrics, create_comparison_chart
from news import get_news_with_sentiment
from styles import apply_custom_styles
import time
import uuid
import html as html_lib

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Apply custom styles
apply_custom_styles()

# Initialize session states
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = set()
if 'insights' not in st.session_state:
    st.session_state.insights = {}
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Header
st.markdown("<h1 class='stock-header'>Stock Analysis Dashboard</h1>", unsafe_allow_html=True)

# User Profile Section in Sidebar
with st.sidebar:
    st.subheader("👤 User Profile")
    if not st.session_state.user_name:
        user_name = st.text_input("Enter your name to share insights")
        if user_name:
            st.session_state.user_name = user_name
            st.success(f"Welcome, {html_lib.escape(user_name)}!")
    else:
        st.write(f"Welcome back, {html_lib.escape(st.session_state.user_name)}!")
        if st.button("Sign Out"):
            st.session_state.user_name = None
            st.rerun()

    st.divider()

    # Watchlist Section
    st.subheader("📋 My Watchlist")

    # Add to watchlist
    new_symbol = st.text_input("Add Stock to Watchlist", key="new_watchlist_symbol").strip().upper()
    if st.button("Add to Watchlist") and new_symbol:
        if new_symbol not in st.session_state.watchlist:
            hist_data, _ = get_stock_data(new_symbol, '1d')
            if hist_data is not None and not hist_data.empty:
                st.session_state.watchlist.add(new_symbol)
                st.success(f"Added {html_lib.escape(new_symbol)} to watchlist!")
            else:
                st.error("Invalid stock symbol")

    # Display watchlist
    st.write("Your Stocks:")
    watchlist_selected = []

    if st.session_state.watchlist:
        for symbol in sorted(st.session_state.watchlist):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.checkbox(symbol, key=f"watch_{symbol}"):
                    watchlist_selected.append(symbol)
            with col2:
                if st.button("🗑️", key=f"del_{symbol}", help=f"Remove {symbol} from watchlist"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()

        # Quick actions
        st.write("---")
        if watchlist_selected:
            if st.button("Compare Selected"):
                stocks_input = ",".join(watchlist_selected)
                st.session_state.comparison_stocks = stocks_input
                st.rerun()
    else:
        st.info("Your watchlist is empty. Add some stocks to track!")

# Input section
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    default_input = getattr(st.session_state, 'comparison_stocks', 'AAPL')
    stocks_input = st.text_input(
        "Enter Stock Symbols (comma-separated, e.g., AAPL, MSFT, GOOGL)",
        value=default_input
    )
    symbols = (
        [sym.strip().upper() for sym in stocks_input.split(',') if sym.strip()]
        if stocks_input else ['AAPL']
    )
with col2:
    period = st.selectbox(
        "Select Time Period",
        options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=3
    )
with col3:
    if st.button("Refresh Data"):
        st.rerun()

# Main content
try:
    stocks_data = {}
    stocks_info = {}
    news_data = {}

    with st.spinner('Fetching data...'):
        for symbol in symbols:
            hist_data, stock_info = get_stock_data(symbol, period)
            if hist_data is not None and not hist_data.empty and stock_info is not None:
                stocks_data[symbol] = hist_data
                stocks_info[symbol] = stock_info
                news_data[symbol] = get_news_with_sentiment(symbol)

    if stocks_data:
        # Comparison Chart
        if len(symbols) > 1:
            st.subheader("Price Comparison")
            st.plotly_chart(create_comparison_chart(stocks_data), use_container_width=True)

        # Individual Stock Analysis
        for symbol in symbols:
            hist_data = stocks_data.get(symbol)
            stock_info = stocks_info.get(symbol)

            if hist_data is not None and stock_info is not None:
                st.markdown("---")

                # Stock Header with Actions
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    safe_name = html_lib.escape(stock_info.get('longName', symbol))
                    safe_symbol = html_lib.escape(symbol)
                    st.subheader(f"{safe_name} ({safe_symbol})")
                    sector = html_lib.escape(stock_info.get('sector', 'N/A'))
                    industry = html_lib.escape(stock_info.get('industry', 'N/A'))
                    st.markdown(f"*{sector} | {industry}*")
                with col2:
                    if symbol not in st.session_state.watchlist:
                        if st.button("➕ Add to Watchlist", key=f"add_watch_{symbol}"):
                            st.session_state.watchlist.add(symbol)
                            st.success(f"Added {safe_symbol} to watchlist!")
                            st.rerun()
                with col3:
                    if st.button("📤 Share Analysis", key=f"share_{symbol}"):
                        # Build a shareable text summary
                        current = hist_data['Close'].iloc[-1]
                        share_text = (
                            f"{safe_name} ({safe_symbol})\n"
                            f"Price: ${current:.2f}\n"
                            f"Sector: {sector} | Industry: {industry}\n"
                            f"Period: {period}"
                        )
                        st.code(share_text, language=None)
                        st.info("Copy the text above to share this analysis.")

                # Current Price and Change — guard against single-row data
                current_price = hist_data['Close'].iloc[-1]
                if len(hist_data) >= 2:
                    prev_price = hist_data['Close'].iloc[-2]
                    price_change = current_price - prev_price
                    price_change_pct = (price_change / prev_price) * 100
                else:
                    price_change = 0.0
                    price_change_pct = 0.0

                price_col, change_col = st.columns(2)
                with price_col:
                    st.metric("Current Price", f"${current_price:.2f}")
                with change_col:
                    st.metric(
                        "Daily Change",
                        f"${price_change:.2f} ({price_change_pct:.2f}%)",
                        delta=price_change
                    )

                # Create tabs for different sections
                tab1, tab2, tab3 = st.tabs(["Technical Analysis", "News & Sentiment", "Community Insights"])

                with tab1:
                    # Price Chart with Patterns
                    st.plotly_chart(create_price_chart(hist_data), use_container_width=True)

                    # Key Metrics
                    st.subheader("Key Metrics")
                    metrics = get_key_metrics(stock_info)
                    cols = st.columns(4)
                    for i, (metric, value) in enumerate(metrics.items()):
                        with cols[i % 4]:
                            safe_metric = html_lib.escape(str(metric))
                            safe_value = html_lib.escape(str(value))
                            st.markdown(f"""
                                <div class='metric-card'>
                                    <h4>{safe_metric}</h4>
                                    <p>{safe_value}</p>
                                </div>
                            """, unsafe_allow_html=True)

                with tab2:
                    # News Section
                    st.subheader("Latest News & Sentiment Analysis")
                    symbol_news = news_data.get(symbol, [])
                    if symbol_news and len(symbol_news) > 0:
                        for item in symbol_news:
                            safe_title = html_lib.escape(item['title'])
                            safe_ts = html_lib.escape(item['timestamp'])
                            with st.expander(f"{safe_title} ({safe_ts})"):
                                st.write(item['summary'])
                                sentiment_color = {
                                    'Positive': 'green',
                                    'Negative': 'red',
                                    'Neutral': 'gray'
                                }.get(item['sentiment'], 'gray')
                                safe_sentiment = html_lib.escape(item['sentiment'])
                                st.markdown(
                                    f"Sentiment: <span style='color: {sentiment_color}'>{safe_sentiment}</span>",
                                    unsafe_allow_html=True
                                )
                    else:
                        st.info("No recent news available for this stock")

                with tab3:
                    # Community Insights Section
                    st.subheader("Community Insights")

                    # Initialize insights for the symbol if not exists
                    if symbol not in st.session_state.insights:
                        st.session_state.insights[symbol] = []

                    # Add new insight
                    if st.session_state.user_name:
                        with st.form(key=f"insight_form_{symbol}"):
                            insight_text = st.text_area("Share your analysis", key=f"insight_{symbol}")
                            sentiment = st.select_slider(
                                "Your sentiment",
                                options=["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"],
                                value="Neutral"
                            )
                            if st.form_submit_button("Share Insight"):
                                if insight_text:
                                    st.session_state.insights[symbol].append({
                                        'id': str(uuid.uuid4()),
                                        'user': st.session_state.user_name,
                                        'text': insight_text,
                                        'sentiment': sentiment,
                                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                                        'likes': 0
                                    })
                                    st.success("Insight shared successfully!")
                    else:
                        st.warning("Please enter your name in the sidebar to share insights")

                    # Display insights
                    if st.session_state.insights[symbol]:
                        for insight in reversed(st.session_state.insights[symbol]):
                            with st.container():
                                safe_user = html_lib.escape(insight['user'])
                                safe_text = html_lib.escape(insight['text'])
                                safe_ts = html_lib.escape(insight['timestamp'])
                                safe_sent = html_lib.escape(insight['sentiment'])
                                st.markdown(f"""
                                    <div style='background-color: #262730; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
                                        <p><strong>{safe_user}</strong> &bull; {safe_ts}</p>
                                        <p>{safe_text}</p>
                                        <p><em>Sentiment: {safe_sent}</em></p>
                                    </div>
                                """, unsafe_allow_html=True)
                                col1, col2 = st.columns([1, 6])
                                with col1:
                                    if st.button(f"👍 {insight['likes']}", key=f"like_{insight['id']}"):
                                        insight['likes'] += 1
                                with col2:
                                    if st.session_state.user_name == insight['user']:
                                        if st.button("🗑️ Delete", key=f"delete_{insight['id']}"):
                                            st.session_state.insights[symbol].remove(insight)
                                            st.rerun()
                    else:
                        st.info("No insights shared yet. Be the first to share your analysis!")

                # Historical Data Table
                st.subheader("Historical Data")
                df_display = hist_data.reset_index()
                df_display['Date'] = df_display['Date'].dt.date
                st.dataframe(df_display.style.format({
                    'Open': '${:.2f}',
                    'High': '${:.2f}',
                    'Low': '${:.2f}',
                    'Close': '${:.2f}',
                    'Volume': '{:,.0f}'
                }), use_container_width=True)

                # Download button
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f"{symbol}_historical_data.csv",
                    mime="text/csv"
                )

    else:
        st.error("Unable to fetch data. Please check the stock symbols and try again.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Data source: Yahoo Finance | Updated: " + time.strftime("%Y-%m-%d %H:%M:%S"))
