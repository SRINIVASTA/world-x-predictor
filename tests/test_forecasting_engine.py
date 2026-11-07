import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.services.forecasting_engine import make_forecast

@patch('src.services.forecasting_engine.yf.Ticker')
@patch('src.services.forecasting_engine.Prophet')
def test_make_forecast_success(mock_prophet_cls, mock_ticker_cls, mock_historical_df, mock_prophet_forecast_df):
    """Verifies baseline metric scaling maps cleanly under non-zero sentiment modifiers."""
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = {"currency": "USD"}
    mock_ticker_instance.history.return_value = mock_historical_df
    mock_ticker_cls.return_value = mock_ticker_instance

    mock_prophet_instance = MagicMock()
    mock_prophet_instance.predict.return_value = mock_prophet_forecast_df
    mock_prophet_cls.return_value = mock_prophet_instance

    # Inject positive sentiment score to test mathematical scaling logic code paths (+0.50)
    sentiment_input = 0.50
    forecast, df, currency, predicted, lower, upper = make_forecast("AAPL", "1 day", sentiment_score=sentiment_input)

    # Calculate expected sentiment scaling formula offsets programmatically
    volatility_multiplier = 0.10
    expected_modifier = 1.0 + (sentiment_input * volatility_multiplier)

    raw_base_predicted = mock_prophet_forecast_df.iloc[-1]['yhat']
    
    assert currency == "$"
    assert predicted == pytest.approx(raw_base_predicted * expected_modifier)
    assert lower <= upper
    mock_prophet_instance.fit.assert_called_once()
