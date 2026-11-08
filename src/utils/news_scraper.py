import feedparser
import urllib.parse
import urllib.request
from datetime import datetime
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    """
    Scrapes the Google News RSS feed for a given asset company/ticker.
    Explicitly fixes the variable assignment glitch on string splits.
    """
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. FIXED: Correctly assign the extracted index 0 string back to query_term
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

    # 2. Structure search query string parameters safely
    encoded_query = urllib.parse.quote(query_term)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    def parse_entries(entries) -> list:
        results = []
        for entry in entries[:max_items]:
            title = entry.get('title', '')
            
            # Extract and parse dynamic publication date timestamps
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

    def fetch_feed_safely(url: str):
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return feedparser.parse(response.read())
        except Exception as fetch_err:
            logger.error(f"HTTP request layer execution drop: {fetch_err}")
            return None

    try:
        # Fetch primary broad query feed context
        feed = fetch_feed_safely(rss_url)
        headlines = parse_entries(feed.entries) if feed else []
        
        # 3. Secure secondary fallback layer if broad term returns empty dataset rows
        if not headlines:
            logger.warning(f"Secondary try fallback executed for stock term: {query_term} stock")
            fallback_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query_term + ' stock')}&hl=en-US&gl=US&ceid=US:en"
            feed = fetch_feed_safely(fallback_url)
            headlines = parse_entries(feed.entries) if feed else []
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to compile RSS dataset matrix: {str(e)}")
        return []
