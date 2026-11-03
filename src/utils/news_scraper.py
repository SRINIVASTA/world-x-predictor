import feedparser
import urllib.parse
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    if name_upper in COMMODITIES_MAP:
        query = COMMODITIES_MAP[name_upper].replace(' ', '+')
    else:
        query = urllib.parse.quote(company_name)
    
    rss_url = f"https://google.com{query}+stock"
    try:
        feed = feedparser.parse(rss_url)
        return [entry['title'] for entry in feed.entries[:max_items]]
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
