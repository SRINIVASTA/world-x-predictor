import feedparser
import urllib.parse
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. Resolve asset names cleanly
    if name_upper in COMMODITIES_MAP:
        query_term = COMMODITIES_MAP[name_upper]
    elif "-" in company_name: 
        # Handle Crypto (e.g., BTC-USD -> BTC)
        query_term = company_name.split("-")[0]
    elif "=" in company_name: 
        # Handle Forex (e.g., EURUSD=X -> EURUSD)
        query_term = company_name.split("=")[0]
    else:
        query_term = company_name

    # 2. Focus the search parameters for an accurate financial digest feed
    refined_query = f"{query_term} stock market business"
    encoded_query = urllib.parse.quote(refined_query)
    
    # ✅ FIXED: Pointed directly to the valid Google News XML engine search path
    rss_url = f"https://google.com{encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        headlines = [entry['title'] for entry in feed.entries[:max_items]]
        
        # 3. Secondary fallback if the compound query yields nothing
        if not headlines:
            logger.warning(f"Secondary try fallback executed for raw term: {query_term}")
            # ✅ FIXED: Corrected the fallback URL path endpoint as well
            fallback_url = f"https://google.com{urllib.parse.quote(query_term)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(fallback_url)
            headlines = [entry['title'] for entry in feed.entries[:max_items]]
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
