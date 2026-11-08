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

# Timeframe dropdown reflecting all settings entries
timeframe = st.sidebar.selectbox(
    "Forecast Timeframe", 
    ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year', '2 year']
)

# --- FIXED NEWS BYPASS LOGIC: Renders news feed even if Groq secret tokens are missing ---
show_news = st.sidebar.checkbox("Show News Feed Layout", value=True)
has_groq = "GROQ_API_KEY" in st.secrets and bool(st.secrets["GROQ_API_KEY"])

if not has_groq:
    st.sidebar.warning("💡 AI Summary deactivated (Missing GROQ_API_KEY). Showing raw news layout text only.")

predict_button = st.sidebar.button("🔮 Predict Price")

# --- FIXED: ALWAYS VISIBLE SIDEBAR DISPATCH FORM ---
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
        # Initialize Core Metrics Pre-Flight
        stock = yf.Ticker(selected_ticker)
        company = stock.info.get("shortName", selected_ticker)
        exchange = detect_exchange(selected_ticker)
        
        # 1️⃣ STEP 1: Pre-fetch Headlines & Execute Groq AI Sentiment Extraction First
        headlines = get_news_headlines(selected_ticker)
        sentiment_score = 0.0  # Baseline fallback default parameter
        market_payload = {}
        
        # 4️⃣ STEP 4: Render News Score Breakdown and Summaries Block
        if show_news and headlines:
            st.markdown("---")
            st.header("📰 Latest News & AI Sentiment Analysis")
            
            col1, col2 = st.columns(2)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                score = market_payload.get("composite_score", 0.0)
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
            st.write(summary_text)
            
            # FIXED: Cache the compiled scores dictionary into session memory alongside other metrics
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
                "headlines": headlines,
                "scores_map": scores_map, # Cached for the light theme PDF generation
                "df": df,              
                "forecast": forecast   
            }
            
        elif show_news and not headlines:
            st.markdown("---")
            st.warning("No recent news found for this ticker asset.")

    except Exception as e:
        st.error(f"❌ Execution error: {e}")

# =====================================================================
# UNIFIED REPORT ENGINE: PASSING THE SCORES MATRIX INTO COMPILATION
# =====================================================================
if st.session_state.last_report_data:
    pdf_filename = "world_x_market_snapshot.pdf"
    data = st.session_state.last_report_data
    
    try:
        df_cached = data["df"]
        forecast_cached = data["forecast"]
        scores_map_cached = data.get("scores_map", {})
        
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import io
        import base64
        
        plt.rcdefaults() 
        fig_pdf, ax = plt.subplots(figsize=(8, 3.5), dpi=200)
        fig_pdf.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#f8fafc')
        
        ax.plot(df_cached['ds'], df_cached['y'], color='#1f77b4', linewidth=2)
        ax.plot(forecast_cached['ds'], forecast_cached['yhat'], color='#ff7f0e', linestyle='--', linewidth=2)
        ax.fill_between(forecast_cached['ds'], forecast_cached['yhat_lower'], forecast_cached['yhat_upper'], color='#ff7f0e', alpha=0.15)
        ax.axvline(x=df_cached['ds'].iloc[-1], color='#33415566', linestyle=':', linewidth=1.5)
        
        ax.set_title(f"Technical Projection Matrix: {data['ticker']}", fontsize=11, color='#0f172a', pad=10, weight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.tick_params(colors='#64748b', labelsize=8)
        ax.grid(True, color='#e2e8f0', linestyle=':', alpha=0.7)
        for spine in ax.spines.values():
            spine.set_color('#cbd5e1')
            
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig_pdf.get_facecolor(), edgecolor='none', bbox_inches='tight')
        buf.seek(0)
        chart_base64_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig_pdf)
        
        # FIXED: Pass the cached scores map dictionary straight to the layout engine
        generate_dashboard_pdf(
            ticker=data["ticker"], company=data["company"], current_p=data["current_p"],
            predicted_p=data["predicted_p"], bound_low=data["bound_low"], bound_high=data["bound_high"],
            sentiment_lbl=data["sentiment_lbl"], sentiment_scr=data["sentiment_scr"], 
            summary_text=data["summary_text"], headlines=data["headlines"],
            scores_map=scores_map_cached, chart_base64=chart_base64_str, output_path=pdf_filename
        )
        
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            
        st.sidebar.markdown("---")
        st.sidebar.subheader("📥 Export Options")
        st.sidebar.download_button(
            label="💾 Download Dashboard PDF",
            data=pdf_bytes,
            file_name=f"WORLDX_{data['ticker']}_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.sidebar.button("📬 Send Email Report", use_container_width=True):
            if not email_receiver_input:
                st.sidebar.error("Please enter at least one recipient email address.")
            else:
                try:
                    email_sender = st.secrets["gmail"]["username"]
                    app_password = st.secrets["gmail"]["app_password"]
                except KeyError:
                    st.sidebar.error("Missing credentials! Verify configuration inside `.streamlit/secrets.toml`.")
                    st.stop()
                
                try:
                    total_sent = send_bulk_report_emails(
                        email_sender=email_sender, app_password=app_password,
                        recipient_input=email_receiver_input, subject=mail_subject,
                        body=mail_body, attachment_path=pdf_filename
                    )
                    st.sidebar.success(f"Email(s) sent successfully to {total_sent} recipient(s)! 🚀")
                except Exception as mail_err:
                    st.sidebar.error(f"Network block active on host firewall: {mail_err}. Use the Download Button above instead!")

        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            
    except Exception as pdf_err:
        st.sidebar.error(f"Error compiling layout preview download asset: {pdf_err}")

st.sidebar.markdown("**Examples for Input:** AAPL, RELIANCE.NS, BTC-USD, EURUSD=X, GC=F, CL=F")
