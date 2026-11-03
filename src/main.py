import os
import sys

# 1. Force Python to recognize the src directory and repo root layout
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 2. Standard Imports
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

from utils.yahoo_search import yahoo_autocomplete_search, extract_ticker
from utils.exchange_detection import detect_exchange
from utils.market_trends import get_recent_trend
from utils.news_scraper import get_news_headlines
from services.forecasting_engine import make_forecast
from services.llm_orchestrator import summarize_news_with_groq

st.set_page_config(page_title="📈 Stock Predictor", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center;'>
        📈 <strong>WORLD-X</strong>: Multi-Asset Price Predictor
    </h1>
    <h3 style='text-align: center; font-weight: normal;'>
        Stocks | Crypto | Forex ₹ | Metals | Crude Oil
    </h3>
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

timeframe = st.sidebar.selectbox("Forecast Timeframe", ['1 day', '1 week', '1 month', '3 months'])

# 3. Securely check Streamlit Secrets for the Groq API key automatically
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

        st.metric("Current Price", f"{currency} {current_price:.2f}", f"{delta:+.2f} ({pct:+.2f}%)")

        st.success(f"📊 Predicted: {currency} {predicted:.2f}")
        st.caption(f"Confidence: {currency} {lower:.2f} - {upper:.2f}")

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

        # 4. Process News Summarization seamlessly using the automated backend token
        if show_news:
            st.markdown("---")
            st.header("📰 Latest News & Summary")

            headlines = get_news_headlines(selected_ticker)
            if not headlines:
                st.warning("No recent news found for this ticker.")
            else:
                st.subheader("Recent Headlines:")
                for h in headlines:
                    st.write(f"• {h}")

                st.info("🧠 Generating news summary using Groq AI...")
                # The orchestrator will read st.secrets["GROQ_API_KEY"] internally
                summary = summarize_news_with_groq(headlines)
                st.markdown("**Summary:**")
                st.write(summary)

    except Exception as e:
        st.error(f"❌ Execution error: {e}")

st.sidebar.markdown(
    """
    **Examples for Input:**  
    AAPL, BTC-USD, EURUSD=X, GC=F, CL=F  
    """
)

st.markdown(
    """
    <hr>
    <div style='color: red; font-size: 0.9rem; max-width: 700px; margin: 20px auto; text-align: justify;'> 
        This application uses predictive architectures for speculative analysis. All data generated is demonstrative and does not constitute financial advice.
    </div>
    """,
    unsafe_allow_html=True
)
