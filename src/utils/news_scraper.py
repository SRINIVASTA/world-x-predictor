import feedparser
import urllib.parse
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. Resolve raw asset base terms (e.g., RELIANCE.NS -> RELIANCE, BTC-USD -> BTC)
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

    # 2. Keep the query simple and clean to ensure high hit rates from the RSS feed
    # Instead of "RELIANCE stock market business", we look for "RELIANCE stock"
    refined_query = f"{query_term} stock"
    encoded_query = urllib.parse.quote(refined_query)
    
    # ✅ CORRECT PATHWAY: Utilizing the verified native search endpoint parameters
    rss_url = f"https://google.com{encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        headlines = [entry['title'] for entry in feed.entries[:max_items]]
        
        # 3. Safe fallback matching parameter using just the raw name
        if not headlines:
            logger.warning(f"Secondary try fallback executed for term: {query_term}")
            fallback_url = f"https://google.com{urllib.parse.quote(query_term)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(fallback_url)
            headlines = [entry['title'] for entry in feed.entries[:max_items]]
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
