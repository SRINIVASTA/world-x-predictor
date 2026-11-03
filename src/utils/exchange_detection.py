import yfinance as yf
from config.logger_config import setup_logger

logger = setup_logger("exchange_detection")

def detect_exchange(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        # Try high-speed structural metadata first
        if hasattr(stock, 'fast_info') and 'exchange' in stock.fast_info:
            return str(stock.fast_info['exchange']).upper()
            
        # Fallback to standard info block mapping
        info = stock.info
        return info.get('exchange', 'UNKNOWN').upper()
    except Exception as e:
        logger.warning(f"Could not resolve exchange asset metadata for {ticker}: {str(e)}")
        return "UNKNOWN"
