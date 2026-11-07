from weasyprint import HTML

def generate_dashboard_pdf(output_path="world_x_desktop_snapshot.pdf"):
    """
    Exclusively compiles the HTML visual structure of the WORLD-X desktop landing page
    and renders it out into a standalone PDF file path.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>WORLD-X Desktop Dashboard</title>
        <style>
            @page {
                size: A4 portrait;
                margin: 15mm;
                @bottom-right {
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 8pt;
                    color: #a0aec0;
                }
            }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 0;
                font-size: 10pt;
            }
            header {
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .header-title { font-size: 22pt; font-weight: 800; color: #3b82f6; margin: 0; }
            .header-subtitle { font-size: 11pt; color: #94a3b8; margin: 5px 0 0 0; }
            .market-grid { display: table; width: 100%; margin-bottom: 25px; border-collapse: separate; border-spacing: 8px; break-inside: avoid; }
            .market-row { display: table-row; }
            .market-card { display: table-cell; background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; width: 20%; text-align: center; }
            .card-name { font-size: 8.5pt; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
            .card-price { font-size: 12pt; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
            .card-change { font-size: 8.5pt; font-weight: 600; }
            .up { color: #10b981; }
            .down { color: #ef4444; }
            .section-title { font-size: 13pt; font-weight: 700; color: #f8fafc; border-left: 4px solid #3b82f6; padding-left: 8px; margin: 20px 0 12px 0; break-after: avoid; }
            .news-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .news-table th { background-color: #1e293b; color: #94a3b8; text-align: left; padding: 10px; font-size: 8.5pt; border-bottom: 2px solid #334155; }
            .news-table td { padding: 12px 10px; border-bottom: 1px solid #334155; vertical-align: top; }
            .news-row { break-inside: avoid; }
            .news-time { font-size: 8pt; color: #64748b; white-space: nowrap; width: 15%; }
            .news-title { font-weight: 600; color: #e2e8f0; margin-bottom: 3px; }
            .news-desc { font-size: 8.5pt; color: #94a3b8; line-height: 1.4; }
            .news-tag { display: inline-block; font-size: 7pt; background-color: #334155; color: #3b82f6; padding: 1px 5px; border-radius: 4px; margin-top: 5px; font-weight: 600; }
        </style>
    </head>
    <body>
        <header>
            <h1 class="header-title">📈 WORLD-X: Multi-Asset Price Predictor</h1>
            <p class="header-subtitle">Stocks | Crypto | Forex ₹ | Metals | Crude Oil — One Platform for Global Markets</p>
        </header>

        <div class="section-title">📊 Live Market Watch</div>
        <div class="market-grid">
            <div class="market-row">
                <div class="market-card"><div class="card-name">Stocks (NIFTY 50)</div><div class="card-price">₹24,315.20</div><div class="card-change up">+0.85%</div></div>
                <div class="market-card"><div class="card-name">Crypto (BTC)</div><div class="card-price">$94,250.00</div><div class="card-change up">+2.41%</div></div>
                <div class="market-card"><div class="card-name">Forex (USD/INR)</div><div class="card-price">₹84.38</div><div class="card-change down">-0.12%</div></div>
                <div class="market-card"><div class="card-name">Metals (Gold)</div><div class="card-price">₹76,450.00</div><div class="card-change up">+0.54%</div></div>
                <div class="market-card"><div class="card-name">Crude Oil</div><div class="card-price">$72.45</div><div class="card-change down">-1.18%</div></div>
            </div>
        </div>

        <div class="section-title">🌍 Global Financial News Feed</div>
        <table class="news-table">
            <thead><tr><th>Time</th><th>Market Update & Sentiment Flow</th></tr></thead>
            <tbody>
                <tr class="news-row">
                    <td class="news-time">10 mins ago</td>
                    <td>
                        <div class="news-title">Federal Reserve Signals Balanced Target Stance for Q4</div>
                        <div class="news-desc">Macroeconomic signals suggest steady yields, prompt adjustments across high-growth stock indexes.</div>
                        <span class="news-tag">STOCKS</span>
                    </td>
                </tr>
                <tr class="news-row">
                    <td class="news-time">45 mins ago</td>
                    <td>
                        <div class="news-title">Bitcoin Consolidation Breaks Out to New Horizons</div>
                        <div class="news-desc">Institutional inflows hit records through spot asset funds, maintaining positive long-term momentum metrics.</div>
                        <span class="news-tag">CRYPTO</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_path)
    return output_path
