import requests
from config.logger_config import setup_logger

logger = setup_logger("yahoo_search")

def yahoo_autocomplete_search(query: str) -> list:
    """
    Queries the Yahoo Finance API to get autocomplete suggestions for tickers.
    """
    if not query:
        return []
        
    try:
        encoded_query = requests.utils.quote(query)
        # ✅ FIXED: Corrected full endpoint path with the matching function variable name
        url = f"https://yahoo.com{encoded_query}&quotesCount=10&newsCount=0"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('quotes', [])
            return [
                f"{q.get('symbol', '')} - {q.get('shortname', '')} ({q.get('exchange', '')})"
                for q in results if q.get('symbol')
            ]
    except Exception as e:
        logger.error(f"Autocomplete network lookup failed: {str(e)}")
    return []

def extract_ticker(value: str) -> str:
    """
    Extracts the raw ticker symbol from the autocomplete string format.
    """
    if " - " in value:
        return value.split(" - ")[0].strip()
    return value.strip()
