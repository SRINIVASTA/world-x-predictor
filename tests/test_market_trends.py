import pytest
import pandas as pd
from src.utils.market_trends import get_recent_trend

def test_get_recent_trend_insufficient_data():
    df = pd.DataFrame({'y': [10, 11, 12]})
    assert get_recent_trend(df) is None

def test_get_recent_trend_positive_momentum():
    # 7 historical low values followed by 7 high values
    data = [10]*7 + [20]*7
    df = pd.DataFrame({'y': data})
    assert get_recent_trend(df) == "positive momentum"
