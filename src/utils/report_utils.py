import os
import smtplib
import time
from weasyprint import HTML
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64

def generate_dashboard_pdf(ticker, company, current_p, predicted_p, bound_low, bound_high, sentiment_lbl, sentiment_scr, summary_text, headlines, scores_map=None, chart_base64=None, output_path="world_x_market_snapshot.pdf"):
    """
    Exclusively compiles live price points, memory chart graphics, and cross-references
    news scraper feeds with AI sentiment scoring data arrays to render a light print-ready PDF.
    """
    ui_color = "#10b981" if sentiment_scr >= 0.25 else "#ef4444" if sentiment_scr <= -0.25 else "#f59e0b"
    scores_map = scores_map or {}
    
    news_rows_html = ""
    if headlines:
        for h in headlines:
            h_title = h.get("title", "") if isinstance(h, dict) else str(h)
            h_date = h.get("date", "Recent") if isinstance(h, dict) else "Recent"
            
            h_clean = h_title.lower().strip()
            individual_score = scores_map.get(h_clean, 0.0)
            
            if h_clean not in scores_map:
                for key, val in scores_map.items():
                    if key in h_clean or h_clean in key:
                        individual_score = val
                        break
            
            badge = "🟢" if individual_score >= 0.20 else "🔴" if individual_score <= -0.20 else "🟡"
            badge_color = "#10b981" if individual_score >= 0.20 else "#ef4444" if individual_score <= -0.20 else "#f59e0b"
            
            news_rows_html += f"""
            <tr style="break-inside: avoid;">
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 8.5pt; color: #64748b; white-space: nowrap; width: 20%;">{h_date}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 9pt; width: 15%; font-weight: bold; color: {badge_color};">
                    {badge} [{individual_score:+.2f}]
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">
                    <div style="font-weight: 600; color: #1e293b; line-height: 1.4;">{h_title}</div>
                </td>
            </tr>
            """
    else:
        news_rows_html = '<tr><td colspan="3" style="padding: 15px; text-align: center; color: #64748b;">No recent news found for this target asset ticker.</td></tr>'

    chart_html = ""
    if chart_base64:
        chart_html = f"""
        <div class="section-title">📊 Technical Projection Matrix Graph</div>
        <div style="text-align: center; margin-bottom: 20px; background-color: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; break-inside: avoid;">
            <img src="data:image/png;base64,{chart_base64}" style="width: 100%; max-height: 280px; border-radius: 4px;" />
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4 portrait; margin: 15mm; @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font-family: 'Segoe UI', Arial, sans-serif; font-size: 8pt; color: #64748b; }} }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #ffffff; color: #1e293b; margin: 0; padding: 0; font-size: 10pt; }}
            header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 15px; margin-bottom: 20px; }}
            .header-title {{ font-size: 22pt; font-weight: 800; color: #1e293b; margin: 0; }}
            .header-subtitle {{ font-size: 11pt; color: #64748b; margin: 5px 0 0 0; }}
            .market-grid {{ display: table; width: 100%; margin-bottom: 25px; border-collapse: separate; border-spacing: 8px; break-inside: avoid; }}
            .market-row {{ display: table-row; }}
            .market-card {{ display: table-cell; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; width: 33%; text-align: center; }}
            .card-name {{ font-size: 9pt; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }}
            .card-price {{ font-size: 14pt; font-weight: 700; color: #0f172a; margin-bottom: 4px; }}
            .section-title {{ font-size: 14pt; font-weight: 700; color: #0f172a; border-left: 4px solid #3b82f6; padding-left: 8px; margin: 25px 0 12px 0; break-after: avoid; }}
            .sentiment-box {{ background-color: #f8fafc; padding: 18px; border-radius: 8px; border-left: 6px solid {ui_color}; border: 1px solid #e2e8f0; margin-bottom: 20px; break-inside: avoid; }}
            .summary-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; line-height: 1.5; color: #334155; margin-bottom: 20px; }}
            .news-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .news-table th {{ background-color: #f8fafc; color: #64748b; text-align: left; padding: 10px; font-size: 8.5pt; border-bottom: 2px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <header>
            <h1 class="header-title">📈 WORLD-X: Multi-Asset Price Predictor</h1>
            <p class="header-subtitle">Stocks | Crypto | Forex ₹ | Metals | Crude Oil — Global Prediction Matrix</p>
        </header>
        <div class="section-title">📊 Active Market Target: {ticker} ({company})</div>
        <div class="market-grid">
            <div class="market-row">
                <div class="market-card"><div class="card-name">Last Close Price</div><div class="card-price">{current_p}</div></div>
                <div class="market-card"><div class="card-name">AI Target Forecast</div><div class="card-price" style="color: #3b82f6;">{predicted_p}</div></div>
                <div class="market-card"><div class="card-name">Confidence Range Bounds</div><div class="card-price" style="font-size: 10pt; padding-top: 4px; color: #0f172a;">{bound_low} — {bound_high}</div></div>
            </div>
        </div>
        <div class="section-title">📰 AI Sentiment Matrix Analytics</div>
        <div class="sentiment-box">
            <div class="card-name">Sentiment Distribution Label</div>
            <div style="font-size: 18pt; font-weight: 700; color: #0f172a; margin: 4px 0;">{sentiment_lbl}</div>
            <div style="font-size: 11pt; color: {ui_color}; font-weight: 600;">Composite Score: {sentiment_scr:+.2f}</div>
        </div>
        <div class="section-title">📝 Executive Summary Insights</div>
        <div class="summary-box">{summary_text}</div>
        {chart_html}
        <div class="section-title">🌍 Live Google RSS News Ingest Feed & Sentiment Breakdown</div>
        <table class="news-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>AI Rating</th>
                    <th>Scraped Market Article Title</th>
                </tr>
            </thead>
            <tbody>{news_rows_html}</tbody>
        </table>
    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_path)
    return output_path


def send_bulk_report_emails(email_sender, app_password, recipient_input, subject, body, attachment_path=None):
    """
    Exclusively handles parsing distinct list endpoints and executing secure delivery loops
    with attached multi-part documentation assets matching your functional pattern requirements.
    """
    recipient_list = [email.strip() for email in recipient_input.split(",") if email.strip()]
    if not recipient_list:
        raise ValueError("Please provide at least one valid recipient address destination.")
    
    # FIXED: Replaced invalid '://gmail.com' string with functional address
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, app_password)
    
    try:
        for receiver in recipient_list:
            # FIXED: Repaired cut-off block and constructed clean multipart payload
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = receiver
            msg['Subject'] = subject
            
            # Attach the email message body text
            msg.attach(MIMEText(body, 'plain'))
            
            # Safely encode and attach the generated PDF report if present
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    msg.attach(part)
            
            server.sendmail(email_sender, receiver, msg.as_string())
            
            # Anti-spam delay pacing
            if len(recipient_list) > 1:
                time.sleep(1)
                
    finally:
        server.quit()
