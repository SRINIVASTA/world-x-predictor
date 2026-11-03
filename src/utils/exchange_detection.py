import yfinance as yf
from config.logger_config import setup_logger

logger = setup_logger("exchange_detection")

def detect_exchange(ticker: str) -> str:
    try:
        info = yf.Ticker(ticker).info
        return info.get('exchange', 'UNKNOWN').upper()
    except Exception as e:
        logger.warning(f"Could not resolve exchange asset metadata for {ticker}: {str(e)}")
        return "UNKNOWN"
