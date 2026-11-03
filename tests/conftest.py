import pytest
import pandas as pd
import datetime

@pytest.fixture
def mock_historical_df():
    """Generates a structured mock yfinance historical dataset."""
    dates = pd.date_range(start="2026-01-01", periods=20, freq="D")
    # Simulate a steady ascending stock chart
    prices = [100.0 + i for i in range(20)]
    df = pd.DataFrame({"Close": prices}, index=dates)
    df.index.name = "Date"
    return df

@pytest.fixture
def mock_prophet_forecast_df():
    """Generates a structured mock dataframe tracking Prophet predictions output shape."""
    dates = pd.date_range(start="2026-01-01", periods=21, freq="D")
    return pd.DataFrame({
        "ds": dates,
        "yhat": [110.0 + i for i in range(21)],
        "yhat_lower": [105.0 + i for i in range(21)],
        "yhat_upper": [115.0 + i for i in range(21)]
    })
