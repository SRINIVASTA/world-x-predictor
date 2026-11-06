import os
import sys

# Force Python execution framework to see paths relative to runtime root
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

from utils.yahoo_search import yahoo_autocomplete_search, extract_ticker
from utils.exchange_detection import detect_exchange
from utils.market_trends import get_recent_trend
from utils.news_scraper import get_news_headlines
from services.forecasting_engine import make_forecast
# ✅ FIXED: Import the unified multi-task sentiment & summary engine
from services.llm_orchestrator import analyze_and_summarize_news

st.set_page_config(page_title="📈 Stock Predictor", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center;'>📈 <strong>WORLD-X</strong>: Multi-Asset Price Predictor</h1>
    <h3 style='text-align: center; font-weight: normal;'>Stocks | Crypto | Forex ₹ | Metals | Crude Oil</h3>
    <p style='text-align: center;'>🌍 One Platform for Global Markets</p>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("🔍 Inputs")
search_input = st.sidebar.text_input("Enter ticker or company name", value="AAPL")

matches = yahoo_autocomplete_search(search_input) if search_input else []
valid_ticker = False
selected_ticker = ""

if matches:
    selected_match = st.sidebar.selectbox("Select a match", matches)
    selected_ticker = extract_ticker(selected_match)
    valid_ticker = True
else:
    selected_ticker = search_input.strip().upper()
    try:
        hist_check = yf.Ticker(selected_ticker).history(period="1d")
        if not hist_check.empty:
            st.sidebar.caption("⚠️ No autocomplete match, using typed input as ticker.")
            valid_ticker = True
        else:
            st.sidebar.warning("❌ No matches found. Ticker may be invalid.")
    except Exception:
        st.sidebar.warning("❌ Invalid input or network error.")

# Timeframe dropdown reflecting all settings entries
timeframe = st.sidebar.selectbox(
    "Forecast Timeframe", 
    ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year', '2 year']
)

show_news = False
if "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"]:
    show_news = st.sidebar.checkbox("Show News & Summary", value=True)
else:
    st.sidebar.error("⚠️ News component disabled: 'GROQ_API_KEY' is missing in Secrets.")

predict_button = st.sidebar.button("🔮 Predict Price")

if predict_button and valid_ticker:
    try:
        stock = yf.Ticker(selected_ticker)
        company = stock.info.get("shortName", selected_ticker)
        exchange = detect_exchange(selected_ticker)

        forecast, df, currency, predicted, lower, upper = make_forecast(selected_ticker, timeframe)

        st.subheader(f"{selected_ticker} ({company})")
        st.write(f"Exchange: `{exchange}`")

        current_price = df['y'].iloc[-1]
        previous_price = df['y'].iloc[-2] if len(df) > 1 else current_price
        delta = current_price - previous_price
        pct = (delta / previous_price) * 100 if previous_price != 0 else 0

        # Formatted using localized currency characters directly 
        st.metric("Current Price", f"{currency}{current_price:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
        st.success(f"📊 Predicted Target: {currency}{predicted:,.2f}")
        st.caption(f"Confidence Bound Range: {currency}{lower:,.2f} — {currency}{upper:,.2f}")

        trend = get_recent_trend(df)
        if trend:
            emoji = "📈" if trend == "positive momentum" else "📉"
            st.info(f"Recent **past trend**: {trend} {emoji}")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['ds'], df['y'], label="Historical", color="blue")
        ax.plot(forecast['ds'], forecast['yhat'], label="Forecast", color="orange")
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='orange', alpha=0.3)
        ax.axvline(df['ds'].iloc[-1], color='gray', linestyle='--', label='Today')
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Price ({currency})")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # 📰 REFACTORED: News & Sentiment Processing Pipeline
        if show_news:
            st.markdown("---")
            st.header("📰 Latest News & AI Sentiment Analysis")
            headlines = get_news_headlines(selected_ticker)
            
            if not headlines:
                st.warning("No recent news found for this ticker.")
            else:
                # Split Layout: News Headlines Left | Sentiment Matrix Right
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Recent Headlines:")
                    for h in headlines:
                        st.write(f"• {h}")
                        
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)  # Align nicely with the subheader
                    with st.spinner("Processing Groq AI Sentiment Matrices..."):
                        # Call our optimized multi-task orchestrator function
                        market_payload = analyze_and_summarize_news(
                            ticker=selected_ticker, 
                            asset_class="Multi-Asset", 
                            headlines=headlines
                        )
                        
                        # Extract and format quantitative indicators
                        score = market_payload.get("composite_score", 0.0)
                        label = market_payload.get("label", "Neutral")
                        
                        # Compute beautiful metric theme color boundaries dynamically
                        ui_color = "#2E7D32" if score >= 0.25 else "#C62828" if score <= -0.25 else "#EF6C00"
                        
                        st.markdown(
                            f"""
                            <div style="background-color:#1E1E1E; padding:18px; border-radius:8px; border-left: 6px solid {ui_color}; margin-top: 10px;">
                                <span style="color:#888; font-size:11px; font-weight:bold; letter-spacing:0.5px; text-transform: uppercase;">AI Sentiment Engine</span>
                                <h3 style="margin:5px 0; color:#FFF; font-size:22px;">{label}</h3>
                                <h4 style="margin:0; color:{ui_color}; font-size:18px;">Score: {score:+.2f}</h4>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                
                # Full-width display for the summarized bullet items
                st.markdown("### 📝 Investor Executive Summary")
                st.write(market_payload.get("summary", "No summary could be parsed."))

    except Exception as e:
        st.error(f"❌ Execution error: {e}")

st.sidebar.markdown("**Examples for Input:** AAPL, RELIANCE.NS, BTC-USD, EURUSD=X, GC=F, CL=F")
