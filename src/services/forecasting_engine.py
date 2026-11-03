import pandas as pd
from prophet import Prophet
import yfinance as yf
from config.base_settings import TIMEFRAME_PERIODS  # ✅ Dropped src.
from config.logger_config import setup_logger        # ✅ Dropped src.

logger = setup_logger("forecasting_engine")

def make_forecast(ticker: str, timeframe: str):
    logger.info(f"Generating forecast for {ticker} over {timeframe}")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        currency = info.get("currency", "USD")

        df = stock.history(period="1y")[["Close"]].reset_index()
        if df.empty:
            raise ValueError(f"No historical data found for ticker: {ticker}")
            
        df.columns = ["ds", "y"]
        df['ds'] = df['ds'].dt.tz_localize(None)

        model = Prophet(daily_seasonality=True)
        model.fit(df)

        periods = TIMEFRAME_PERIODS.get(timeframe, 1)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        predicted = forecast.iloc[-1]['yhat']
        lower = forecast.iloc[-1]['yhat_lower']
        upper = forecast.iloc[-1]['yhat_upper']

        return forecast, df, currency, predicted, lower, upper
    except Exception as e:
        logger.error(f"Failed to generate forecast for {ticker}: {str(e)}")
        raise
