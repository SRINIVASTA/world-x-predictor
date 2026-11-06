import feedparser
import urllib.parse
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. Strip country indicators or extensions cleanly (e.g., RELIANCE.NS -> RELIANCE)
    if name_upper in COMMODITIES_MAP:
        query_term = COMMODITIES_MAP[name_upper]
    elif "-" in company_name: 
        query_term = company_name.split("-")[0]
    elif "=" in company_name: 
        query_term = company_name.split("=")[0]
    elif "." in company_name:
        query_term = company_name.split(".")[0]
    else:
        query_term = company_name

    # 2. Keep the query keyword format balanced and optimized (e.g., "RELIANCE stock")
    refined_query = f"{query_term} stock"
    encoded_query = urllib.parse.quote(refined_query)
    
    # ✅ FIXED: Corrected the full news.google.com subdomain and explicit search path structure
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        headlines = [entry['title'] for entry in feed.entries[:max_items]]
        
        # 3. Secure secondary fallback query layer using only the raw asset name
        if not headlines:
            logger.warning(f"Secondary try fallback executed for raw term: {query_term}")
            fallback_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query_term)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(fallback_url)
            headlines = [entry['title'] for entry in feed.entries[:max_items]]
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
