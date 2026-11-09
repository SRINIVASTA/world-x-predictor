import pytest
from unittest.mock import patch, MagicMock
from src.utils.exchange_detection import detect_exchange

@pytest.fixture
def mock_yfinance():
    """Fixture to cleanly mock out the yfinance Ticker creation layer."""
    with patch("src.utils.exchange_detection.yf.Ticker") as mock_ticker_class:
        mock_stock_instance = MagicMock()
        mock_ticker_class.return_value = mock_stock_instance
        yield mock_stock_instance


def test_detect_exchange_via_fast_info(mock_yfinance):
    """Verifies that high-speed fast_info metadata is preferred and capitalized correctly."""
    mock_stock = mock_yfinance
    
    # Configure mock object to mimic the fast_info property layout
    mock_fast_info = {"exchange": "NMS"}  # e.g., NASDAQ Global Market
    mock_stock.fast_info = mock_fast_info
    
    # Act
    exchange = detect_exchange("AAPL")
    
    # Assert
    assert exchange == "NMS"
    # Ensure it didn't call the heavy .info dictionary due to short-circuiting
    mock_stock.info.get.assert_not_called()


def test_detect_exchange_fallback_to_standard_info(mock_yfinance):
    """Verifies fallback to the classic info block if fast_info doesn't contain exchange keys."""
    mock_stock = mock_yfinance
    
    # Simulate missing exchange key in fast_info
    mock_stock.fast_info = {} 
    # Configure traditional info lookup dictionary responses
    mock_stock.info = {"exchange": "nys"}  # Lowercase to test uppercase enforcement
    
    # Act
    exchange = detect_exchange("NYSE:T")
    
    # Assert
    assert exchange == "NYS"


def test_detect_exchange_missing_metadata_returns_unknown(mock_yfinance):
    """Ensures that if metadata blocks don't hold an exchange reference, UNKNOWN is returned."""
    mock_stock = mock_yfinance
    
    mock_stock.fast_info = {}
    mock_stock.info = {}  # Empty response
    
    # Act
    exchange = detect_exchange("INVALID_TICKER")
    
    # Assert
    assert exchange == "UNKNOWN"


@patch("src.utils.exchange_detection.logger")
def test_detect_exchange_exception_handling(mock_logger, mock_yfinance):
    """Verifies that network errors or API contract violations are caught safely and logged."""
    # Force yfinance instantiation to raise a network exception
    with patch("src.utils.exchange_detection.yf.Ticker", side_effect=Exception("API Connection Timeout")):
        
        # Act
        exchange = detect_exchange("RELIANCE.NS")
        
        # Assert
        assert exchange == "UNKNOWN"
        # Validate that the logger warning block was notified about the breakdown
        mock_logger.warning.assert_called_once()
        assert "Could not resolve exchange asset metadata for RELIANCE.NS" in mock_logger.warning.call_args[0][0]
