import requests
from config.logger_config import setup_logger

logger = setup_logger("yahoo_search")

def yahoo_autocomplete_search(query: str) -> list:
    """
    Queries the internal Yahoo Finance API to get accurate autocomplete suggestions.
    """
    if not query:
        return []
        
    encoded_query = requests.utils.quote(query)
    # ✅ FIXED: Corrected full subdomain and specific v1 search matrix route
    url = f"https://yahoo.com{encoded_query}&quotesCount=10&newsCount=0"
    
    try:
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
    return value.split(" - ")[0].strip() if " - " in value else value.strip()
