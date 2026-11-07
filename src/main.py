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

# Import modular background reporting utilities
from utils.report_utils import generate_dashboard_pdf, send_bulk_report_emails

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

# --- INTEGRATED SIDEBAR BULK DISPATCH FORM ---
st.sidebar.markdown("---")
st.sidebar.subheader("✉️ Automated PDF Dispatch")
email_receiver_input = st.sidebar.text_input('Recipient Email(s) (separate with commas)')
mail_subject = st.sidebar.text_input('Mail Subject', value="WORLD-X Market Analytics Report")
mail_body = st.sidebar.text_area('Mail Body', value="Please review the attached multi-asset analytics target document compiled from your dashboard.")

# Initialize dynamic reporting memory cache
if "last_report_data" not in st.session_state:
    st.session_state.last_report_data = None
if predict_button and valid_ticker:
    try:
        stock = yf.Ticker(selected_ticker)
        company = stock.info.get("shortName", selected_ticker)
        exchange = detect_exchange(selected_ticker)
        
        # Pull headlines dynamically using your optimized news_scraper module logic
        headlines = get_news_headlines(selected_ticker)
        sentiment_score = 0.0  
        market_payload = {}
        
        if show_news and headlines:
            raw_headlines_strings = [h.get("title", "") if isinstance(h, dict) else str(h) for h in headlines]
            with st.spinner("Processing Groq AI Sentiment Matrices..."):
                market_payload = analyze_and_summarize_news(
                    ticker=selected_ticker, 
                    asset_class="Multi-Asset", 
                    headlines=raw_headlines_strings
                )
                sentiment_score = market_payload.get("composite_score", 0.0)

        forecast, df, currency, predicted, lower, upper = make_forecast(
            ticker=selected_ticker, 
            timeframe=timeframe, 
            sentiment_score=sentiment_score
        )

        current_price = df['y'].iloc[-1]
        previous_price = df['y'].iloc[-2] if len(df) > 1 else current_price
        delta = current_price - previous_price
        pct = (delta / previous_price) * 100 if previous_price != 0 else 0
        
        label = market_payload.get("label", "Neutral")
        summary_text = market_payload.get("summary", "No analytical content found.")
        
        # Caches clean structures containing dynamic string news arrays
        st.session_state.last_report_data = {
            "ticker": selected_ticker,
            "company": company,
            "current_p": f"{currency}{current_price:,.2f}",
            "predicted_p": f"{currency}{predicted:,.2f}",
            "bound_low": f"{currency}{lower:,.2f}",
            "bound_high": f"{currency}{upper:,.2f}",
            "sentiment_lbl": label,
            "sentiment_scr": sentiment_score,
            "summary_text": summary_text,
            "headlines": headlines  # Passes active live news data objects directly
        }

        st.subheader(f"{selected_ticker} ({company})")
        st.write(f"Exchange: `{exchange}`")
        st.metric("Current Price", f"{currency}{current_price:,.2f}", f"{delta:+.2f} ({pct:+.2f}%)")
        st.success(f"📊 Predicted Target: {currency}{predicted:,.2f}")
        st.caption(f"Confidence Bound Range (Sentiment-Adjusted): {currency}{lower:,.2f} — {currency}{upper:,.2f}")

        trend = get_recent_trend(df)
        if trend:
            emoji = "📈" if trend == "positive momentum" else "📉"
            st.info(f"Recent **past trend**: {trend} {emoji}")

        # Plotly Graph Layout
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Historical Close", line=dict(color="#1f77b4", width=2.5)))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="AI Target Forecast", line=dict(color="#ff7f0e", width=2.5, dash="dash")))

        forecast_ds = forecast['ds'].tolist()
        upper_list = [float(x) for x in forecast['yhat_upper']]
        lower_list = [float(x) for x in forecast['yhat_lower']]

        fig.add_trace(go.Scatter(x=forecast_ds, y=upper_list, line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(
            x=forecast_ds, y=lower_list, fill='tonexty', fillcolor='rgba(255, 127, 14, 0.12)', line=dict(width=0), 
            name="Confidence Range", customdata=list(zip(lower_list, upper_list))
        ))

        fig.update_layout(
            title=dict(text=f"Interactive Technical Projection Matrix: {selected_ticker}", font=dict(size=16, color="#FFF")),
            xaxis_title="Timeline", yaxis_title=f"Asset Valuation Value ({currency})", hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

        if show_news and headlines:
            st.markdown("---")
            st.header("📰 Latest News & AI Sentiment Analysis")
            col1, col2 = st.columns(2)
            
            with col2:
                score = market_payload.get("composite_score", 0.0)
                ui_color = "#2E7D32" if score >= 0.25 else "#C62828" if score <= -0.25 else "#EF6C00"
                st.markdown(f'<div style="background-color:#1E1E1E; padding:18px; border-radius:8px; border-left: 6px solid {ui_color};"><h3>{label}</h3><h4>Score: {score:+.2f}</h4></div>', unsafe_allow_html=True)

            with col1:
                st.subheader("Recent Headlines & Score Breakdown:")
                breakdown_list = market_payload.get("breakdown", [])
                scores_map = {item.get("headline", "").lower().strip(): item.get("score", 0.0) for item in breakdown_list}
                
                for h in headlines:
                    h_title = h.get("title", "") if isinstance(h, dict) else str(h)
                    ind_score = scores_map.get(h_title.lower().strip(), 0.0)
                    badge = "🟢" if ind_score >= 0.20 else "🔴" if ind_score <= -0.20 else "🟡"
                    st.markdown(f"{badge} **[{ind_score:+.2f}]** {h_title}")
            
            st.markdown("### 📝 Investor Executive Summary")
            st.write(summary_text)

    except Exception as e:
        st.error(f"❌ Execution error: {e}")

# --- EMAIL DISPATCH ACTION TRIGGER ---
if st.sidebar.button("📬 Send Email Report"):
    if not st.session_state.last_report_data:
        st.sidebar.error("Please execute a price prediction calculation first to compile data maps.")
    elif not email_receiver_input:
        st.sidebar.error("Please enter at least one recipient email address.")
    else:
        try:
            email_sender = st.secrets["gmail"]["username"]
            app_password = st.secrets["gmail"]["app_password"]
        except KeyError:
            st.sidebar.error("Missing credentials! Check configurations inside `.streamlit/secrets.toml`.")
            st.stop()

        try:
            pdf_filename = "world_x_market_snapshot.pdf"
            data = st.session_state.last_report_data
            
            # Module A execution call passing dynamic headlines array securely
            generate_dashboard_pdf(
                ticker=data["ticker"], company=data["company"], current_p=data["current_p"],
                predicted_p=data["predicted_p"], bound_low=data["bound_low"], bound_high=data["bound_high"],
                sentiment_lbl=data["sentiment_lbl"], sentiment_scr=data["sentiment_scr"], 
                summary_text=data["summary_text"], headlines=data["headlines"], output_path=pdf_filename
            )
            
            # Module B execution call
            total_sent = send_bulk_report_emails(
                email_sender=email_sender, app_password=app_password,
                recipient_input=email_receiver_input, subject=mail_subject,
                body=mail_body, attachment_path=pdf_filename
            )
            
            if os.path.exists(pdf_filename):
                os.remove(pdf_filename)
                
            st.sidebar.success(f"Email(s) dispatched successfully to {total_sent} recipient(s)! 🚀")
        except Exception as mail_err:
            st.sidebar.error(f"Erreur lors de l’envoi de l’e-mail : {mail_err}")

st.sidebar.markdown("**Examples for Input:** AAPL, RELIANCE.NS, BTC-USD, EURUSD=X, GC=F, CL=F")
