import pytest
from unittest.mock import patch, MagicMock
from src.utils.yahoo_search import yahoo_autocomplete_search, extract_ticker

@pytest.fixture
def mock_requests():
    """Fixture to cleanly mock out the requests network transport layer."""
    with patch("src.utils.yahoo_search.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        yield mock_get, mock_response


# ==========================================
# PART 1: yahoo_autocomplete_search Tests
# ==========================================

def test_yahoo_autocomplete_empty_query():
    """Ensures empty strings instantly return an empty list without firing network requests."""
    with patch("src.utils.yahoo_search.requests.get") as mock_get:
        results = yahoo_autocomplete_search("")
        assert results == []
        mock_get.assert_not_called()


def test_yahoo_autocomplete_success(mock_requests):
    """Verifies that valid API responses are parsed cleanly into unified ticker target formats."""
    mock_get, mock_response = mock_requests
    
    # Configure successful response state
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "quotes": [
            {"symbol": "RELIANCE.NS", "shortname": "Reliance Industries", "exchange": "NSE"},
            {"symbol": "AAPL", "shortname": "Apple Inc.", "exchange": "NMS"},
            {"symbol": "INVALID"}  # Missing shortname/exchange should fall back to empty strings gracefully
        ]
    }
    
    # Act
    results = yahoo_autocomplete_search("Reliance")
    
    # Assert
    assert len(results) == 3
    assert results[0] == "RELIANCE.NS - Reliance Industries (NSE)"
    assert results[1] == "AAPL - Apple Inc. (NMS)"
    assert results[2] == "INVALID -  ()"  # Checked safe dict structural fallbacks
    mock_get.assert_called_once()


def test_yahoo_autocomplete_non_200_status(mock_requests):
    """Verifies that non-200 HTTP response codes are caught and return an empty result gracefully."""
    _, mock_response = mock_requests
    mock_response.status_code = 500  # Internal Server Error simulation
    
    # Act
    results = yahoo_autocomplete_search("BTC")
    
    # Assert
    assert results == []


@patch("src.utils.yahoo_search.logger")
def test_yahoo_autocomplete_network_exception(mock_logger, mock_requests):
    """Verifies that request dropouts or timeouts are logged and safely suppressed."""
    mock_get, _ = mock_requests
    # Force requests to drop connection completely
    mock_get.side_effect = Exception("Connection Refused / Timeout")
    
    # Act
    results = yahoo_autocomplete_search("NIFTY")
    
    # Assert
    assert results == []
    # Verify the engineering logging layers were notified of the network failure
    mock_logger.error.assert_called_once()
    assert "Autocomplete network lookup failed" in mock_logger.error.call_args[0][0]


# ==========================================
# PART 2: extract_ticker Tests
# ==========================================

@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("RELIANCE.NS - Reliance Industries (NSE)", "RELIANCE.NS"),
        ("BTC-USD - Bitcoin USD (CCC)", "BTC-USD"),
        ("AAPL", "AAPL"),                  # Case where no delimiter is found
        ("  INFY.NS - Infosys  (NSE) ", "INFY.NS"),  # Verifies strict whitespace stripping
        ("NIFTY 50 - ", "NIFTY 50"),        # Trailing separator edge case
    ]
)
def test_extract_ticker_variations(input_value, expected_output):
    """Validates string manipulation rules across standard autocomplete blocks and raw ticker fallbacks."""
    assert extract_ticker(input_value) == expected_output
