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
import plotly.graph_objects as go

from utils.yahoo_search import yahoo_autocomplete_search, extract_ticker
from utils.exchange_detection import detect_exchange
from utils.market_trends import get_recent_trend
from utils.news_scraper import get_news_headlines
from services.forecasting_engine import make_forecast
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
        # Initialize Core Metrics Pre-Flight
        stock = yf.Ticker(selected_ticker)
        company = stock.info.get("shortName", selected_ticker)
        exchange = detect_exchange(selected_ticker)
        
        # 1️⃣ STEP 1: Pre-fetch Headlines & Execute Groq AI Sentiment Extraction First
        headlines = get_news_headlines(selected_ticker)
        sentiment_score = 0.0  # Baseline fallback default parameter
        market_payload = {}
        
        if show_news and headlines:
            # Convert dict models to raw string tokens safely for Groq Context
            raw_headlines_strings = [h.get("title", "") if isinstance(h, dict) else str(h) for h in headlines]
            
            with st.spinner("Processing Groq AI Sentiment Matrices..."):
                market_payload = analyze_and_summarize_news(
                    ticker=selected_ticker, 
                    asset_class="Multi-Asset", 
                    headlines=raw_headlines_strings
                )
                sentiment_score = market_payload.get("composite_score", 0.0)

        # 2️⃣ STEP 2: Feed the Live Sentiment Modifier Score straight into Prophet Mathematical Pipeline
        forecast, df, currency, predicted, lower, upper = make_forecast(
            ticker=selected_ticker, 
            timeframe=timeframe, 
            sentiment_score=sentiment_score
        )

        # 3️⃣ STEP 3: Render Primary Visual Layouts
        st.subheader(f"{selected_ticker} ({company})")
        st.write(f"Exchange: `{exchange}`")

        current_price = df['y'].iloc[-1]
        previous_price = df['y'].iloc[-2] if len(df) > 1 else current_price
        delta = current_price - previous_price
        pct = (delta / previous_price) * 100 if previous_price != 0 else 0

        st.metric("Current Price", f"{currency}{current_price:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
        st.success(f"📊 Predicted Target: {currency}{predicted:,.2f}")
        st.caption(f"Confidence Bound Range (Sentiment-Adjusted): {currency}{lower:,.2f} — {currency}{upper:,.2f}")

        trend = get_recent_trend(df)
        if trend:
            emoji = "📈" if trend == "positive momentum" else "📉"
            st.info(f"Recent **past trend**: {trend} {emoji}")

        # 📊 REFACTORED: Interactive Hover Plotly Chart Generation
        fig = go.Figure()

        # A. Historical Closing Prices Line Trace
        fig.add_trace(go.Scatter(
            x=df['ds'], 
            y=df['y'], 
            name="Historical Close",
            line=dict(color="#1f77b4", width=2.5),
            hovertemplate=f"Price: {currency}%{{y:,.2f}}<extra></extra>"
        ))

        # B. Prophet Center Forecast Line Trace
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=forecast['yhat'], 
            name="AI Target Forecast",
            line=dict(color="#ff7f0e", width=2.5, dash="dash"),
            hovertemplate=f"Predicted: {currency}%{{y:,.2f}}<extra></extra>"
        ))

        # C. Sentiment-Adjusted Confidence Bound Bounds (Shaded Area Traces)
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=upper, 
            line=dict(width=0), 
            showlegend=False, 
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=lower, 
            fill='tonexty', 
            fillcolor='rgba(255, 127, 14, 0.12)', 
            line=dict(width=0), 
            name="Confidence Range",
            hovertemplate=f"Max Range: {currency}%{{customdata[1]:,.2f}}<br>Min Range: {currency}%{{customdata[0]:,.2f}}<extra></extra>",
            customdata=list(zip(lower, upper))
        ))

        # D. Vertical Reference Flag for "Today" Axis
        fig.add_shape(
            type="line",
            x0=df['ds'].iloc[-1], y0=df['y'].min() * 0.9,
            x1=df['ds'].iloc[-1], y1=upper.max() * 1.1,
            line=dict(color="rgba(255,255,255,0.4)", width=1.5, dash="dot"),
        )

        # E. Global Layout Theme Options Initialization
        fig.update_layout(
            title=dict(text=f"Interactive Technical Projection Matrix: {selected_ticker}", font=dict(size=16, color="#FFF")),
            xaxis_title="Timeline Timeline",
            yaxis_title=f"Asset Valuation Value ({currency})",
            hovermode="x unified",  # Locks tooltips together onto a single crosshair box layout on hover
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=45, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridcolor="#2D2D2D"),
            yaxis=dict(showgrid=True, gridcolor="#2D2D2D", tickformat=",.2f")
        )

        st.plotly_chart(fig, use_container_width=True)

        # 4️⃣ STEP 4: Render News Score Breakdown and Summaries Block
        if show_news and headlines:
            st.markdown("---")
            st.header("📰 Latest News & AI Sentiment Analysis")
            
            col1, col2 = st.columns(2)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                score = market_payload.get("composite_score", 0.0)
                label = market_payload.get("label", "Neutral")
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

            with col1:
                st.subheader("Recent Headlines & Score Breakdown:")
                
                breakdown_list = market_payload.get("breakdown", [])
                scores_map = {}
                for item in breakdown_list:
                    scores_map[item.get("headline", "").lower().strip()] = item.get("score", 0.0)
                
                for h in headlines:
                    if isinstance(h, dict):
                        h_title = h.get("title", "")
                        h_date = f" *({h.get('date', 'N/A')})*"
                    else:
                        h_title = str(h)
                        h_date = ""
                        
                    h_clean = h_title.lower().strip()
                    individual_score = scores_map.get(h_clean, 0.0)
                    
                    if h_clean not in scores_map:
                        for key, val in scores_map.items():
                            if key in h_clean or h_clean in key:
                                    individual_score = val
                                    break
                    
                    badge = "🟢" if individual_score >= 0.20 else "🔴" if individual_score <= -0.20 else "🟡"

                    st.markdown(f"{badge} **[{individual_score:+.2f}]**{h_date} {h_title}")
            
            st.markdown("### 📝 Investor Executive Summary")
            st.write(market_payload.get("summary", "No summary could be parsed."))
            
        elif show_news and not headlines:
            st.markdown("---")
            st.warning("No recent news found for this ticker asset.")

    except Exception as e:
        st.error(f"❌ Execution error: {e}")

st.sidebar.markdown("**Examples for Input:** AAPL, RELIANCE.NS, BTC-USD, EURUSD=X, GC=F, CL=F")
