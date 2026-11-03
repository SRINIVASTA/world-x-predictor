import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.services.forecasting_engine import make_forecast

@patch('src.services.forecasting_engine.yf.Ticker')
@patch('src.services.forecasting_engine.Prophet')
def test_make_forecast_success(mock_prophet_cls, mock_ticker_cls, mock_historical_df, mock_prophet_forecast_df):
    # Arrange Mock Ticker
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = {"currency": "INR"}
    mock_ticker_instance.history.return_value = mock_historical_df
    mock_ticker_cls.return_value = mock_ticker_instance

    # Arrange Mock Prophet Pipeline
    mock_prophet_instance = MagicMock()
    mock_prophet_instance.predict.return_value = mock_prophet_forecast_df
    mock_prophet_cls.return_value = mock_prophet_instance

    # Act
    forecast, df, currency, predicted, lower, upper = make_forecast("RELIANCE.NS", "1 day")

    # Assert
    assert currency == "INR"
    assert not df.empty
    assert "ds" in df.columns
    assert "y" in df.columns
    # Ensure timezone localization logic stripped the tz data clean
    assert df['ds'].dt.tz is None 
    
    # Assert forecast structural bounds
    assert predicted == mock_prophet_forecast_df.iloc[-1]['yhat']
    assert lower == mock_prophet_forecast_df.iloc[-1]['yhat_lower']
    assert upper == mock_prophet_forecast_df.iloc[-1]['yhat_upper']
    
    # Validate Prophet operations were triggered correctly
    mock_prophet_instance.fit.assert_called_once()
    mock_prophet_instance.predict.assert_called_once()

@patch('src.services.forecasting_engine.yf.Ticker')
def test_make_forecast_empty_ticker_data(mock_ticker_cls):
    # Arrange ticker to return an empty dataframe simulation
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.return_value = pd.DataFrame()
    mock_ticker_cls.return_value = mock_ticker_instance

    # Act & Assert
    with pytest.raises(ValueError, match="No historical data found for ticker"):
        make_forecast("INVALID", "1 day")
