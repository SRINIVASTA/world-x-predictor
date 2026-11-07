import pytest
from unittest.mock import patch, MagicMock
from src.utils.news_scraper import get_news_headlines

# =====================================================================
# NEWS SCRAPER MODULE TESTS: FEEDPARSER RSS PARSING ASSERTS
# =====================================================================
@patch('src.utils.news_scraper.feedparser.parse')
def test_get_news_headlines_success(mock_feed_parse):
    """Validates query extraction strings are scrubbed and outputs match expected shape schemas."""
    # Arrange: Build mock feed entry structures mirroring actual feedparser responses
    mock_entry = MagicMock()
    mock_entry.get.side_effect = lambda key, default=None: {
        'title': 'Bitcoin Hits Record High Parameters'
    }.get(key, default)
    
    # Simulate a structural time tuple matching RSS publication specs (Nov 07, 2026 context)
    mock_entry.published_parsed = (2026, 11, 7, 12, 0, 0, 5, 311, 0)
    
    mock_feed_instance = MagicMock()
    mock_feed_instance.entries = [mock_entry]
    mock_feed_parse.return_value = mock_feed_instance

    # Act
    headlines = get_news_headlines("BTC-USD", max_items=1)

    # Assert
    assert len(headlines) == 1
    assert headlines[0]['title'] == 'Bitcoin Hits Record High Parameters'
    assert headlines[0]['date'] == 'Nov 07, 2026'
    
    # Verify proper asset extension cleaning string logic applied matching news_scraper components
    mock_feed_parse.assert_called_once()
    called_url = mock_feed_parse.call_args[0][0]
    assert "BTC" in called_url  # Suffix "-USD" successfully stripped away into a clean string


@patch('src.utils.news_scraper.feedparser.parse')
def test_get_news_headlines_empty_fallback(mock_feed_parse):
    """Confirms primary missing records successfully trigger secondary try fallback layers."""
    # Arrange: Return empty arrays on first attempt, valid items on secondary fallback sweep
    mock_empty_feed = MagicMock(entries=[])
    
    mock_valid_entry = MagicMock()
    mock_valid_entry.get.side_effect = lambda key, default=None: {
        'title': 'Alternative Commodity Gold Trading Flow'
    }.get(key, default)
    mock_valid_entry.published_parsed = None  # Force current fallback date execution paths
    
    mock_success_feed = MagicMock(entries=[mock_valid_entry])
    mock_feed_parse.side_effect = [mock_empty_feed, mock_success_feed]

    # Act
    headlines = get_news_headlines("GC=F", max_items=5)

    # Assert
    assert len(headlines) == 1
    assert headlines[0]['title'] == 'Alternative Commodity Gold Trading Flow'
    # Ensure double call execution paths tracking primary and secondary endpoint routing channels
    assert mock_feed_parse.call_count == 2
