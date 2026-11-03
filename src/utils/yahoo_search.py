import requests
from ..config.logger_config import setup_logger

logger = setup_logger("yahoo_search")

def yahoo_autocomplete_search(query: str) -> list:
    url = f"https://yahoo.com{query}&quotesCount=10&newsCount=0"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('quotes', [])
            return [
                f"{q.get('symbol', '')} - {q.get('shortname', '')} ({q.get('exchange', '')})"
                for q in results
            ]
    except Exception as e:
        logger.error(f"Autocomplete network lookup timed out or failed: {str(e)}")
    return []

def extract_ticker(value: str) -> str:
    return value.split(" - ")[0].strip() if " - " in value else value.strip()
