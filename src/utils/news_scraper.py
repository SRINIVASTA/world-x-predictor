import feedparser
import urllib.parse
from datetime import datetime
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    """
    Scrapes the Google News RSS feed for a given asset company/ticker.
    Cleans up input string extensions, falls back safely to broad terms,
    and returns a clean payload array mapped for the PDF dispatch pipelines.
    """
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. Strip country indicators, marketplace markers, or exchange suffixes cleanly
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

    # 2. Broadened query keyword format: Search for the asset identifier directly
    encoded_query = urllib.parse.quote(query_term)
    rss_url = f"https://google.com{encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    def parse_entries(entries) -> list:
        results = []
        for entry in entries[:max_items]:
            title = entry.get('title', '')
            
            # Extract RSS timestamps structure mappings securely
            date_str = ""
            published_parsed = entry.get('published_parsed')
            
            if published_parsed:
                try:
                    date_str = datetime(*published_parsed[:6]).strftime("%b %d, %Y")
                except Exception:
                    date_str = datetime.now().strftime("%b %d, %Y")
            else:
                date_str = datetime.now().strftime("%b %d, %Y")
                
            if title:
                results.append({
                    "title": title,
                    "date": date_str
                })
        return results

    try:
        # Run execution loop on the broad query parameters
        feed = feedparser.parse(rss_url)
        headlines = parse_entries(feed.entries)
        
        # 3. Secure secondary fallback query layer using refined "stock" term if broad term returns zero
        if not headlines:
            logger.warning(f"Secondary try fallback executed for stock term: {query_term} stock")
            fallback_url = f"https://google.com{urllib.parse.quote(query_term + ' stock')}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(fallback_url)
            headlines = parse_entries(feed.entries)
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
