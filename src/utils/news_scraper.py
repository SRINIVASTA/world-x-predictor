import feedparser
import urllib.parse
import urllib.request
from datetime import datetime
from config.base_settings import COMMODITIES_MAP
from config.logger_config import setup_logger

logger = setup_logger("news_scraper")

def get_news_headlines(company_name: str, max_items: int = 5) -> list:
    logger.info(f"Initiating remote RSS ingest tracking query for: {company_name}")
    name_upper = company_name.upper()
    
    # 1. Strip country indicators or extensions cleanly (Your exact working layout)
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

    # 2. Keep the query keyword format balanced and optimized
    refined_query = f"{query_term} stock"
    encoded_query = urllib.parse.quote(refined_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    def parse_entries(entries) -> list:
        results = []
        for entry in entries[:max_items]:
            title = entry.get('title', '')
            
            # Extract RSS time structure mapping elements safely
            date_str = ""
            published_parsed = entry.get('published_parsed')
            
            if published_parsed:
                try:
                    # Convert structural time tuples natively to a standardized format
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

    def fetch_feed_with_agent(url: str):
        """Injects browser user-agent headers to prevent Google News endpoint blocking."""
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return feedparser.parse(response.read())
        except Exception as e:
            logger.error(f"Network request connection failed for endpoint: {str(e)}")
            return None

    try:
        # Fetch primary news payload with headers
        feed = fetch_feed_with_agent(rss_url)
        headlines = parse_entries(feed.entries) if feed else []
        
        # 3. Secure secondary fallback query layer using only the raw asset name
        if not headlines:
            logger.warning(f"Secondary try fallback executed for raw term: {query_term}")
            fallback_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query_term)}&hl=en-US&gl=US&ceid=US:en"
            feed = fetch_feed_with_agent(fallback_url)
            headlines = parse_entries(feed.entries) if feed else []
            
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed from endpoint: {str(e)}")
        return []
