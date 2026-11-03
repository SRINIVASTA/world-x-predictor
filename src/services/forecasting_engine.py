import pandas as pd
from prophet import Prophet
import yfinance as yf
from config.base_settings import TIMEFRAME_PERIODS, get_currency_symbol
from config.logger_config import setup_logger

logger = setup_logger("forecasting_engine")

def make_forecast(ticker: str, timeframe: str):
    logger.info(f"Generating forecast for {ticker} over {timeframe}")
    try:
        stock = yf.Ticker(ticker)
        
        # Securely parse raw local currency identifiers
        raw_currency = "USD"
        if hasattr(stock, 'fast_info') and 'currency' in stock.fast_info:
            raw_currency = stock.fast_info['currency']
        else:
            raw_currency = stock.info.get("currency", "USD")
            
        # Map ISO code to its localized symbol representation
        currency_symbol = get_currency_symbol(raw_currency)

        df = stock.history(period="1y")[["Close"]].reset_index()
        if df.empty:
            raise ValueError(f"No historical data found for ticker: {ticker}")
            
        df.columns = ["ds", "y"]
        df['ds'] = df['ds'].dt.tz_localize(None)

        model = Prophet(daily_seasonality=True)
        model.fit(df)

        periods = TIMEFRAME_PERIODS.get(timeframe, 90)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        predicted = forecast.iloc[-1]['yhat']
        lower = forecast.iloc[-1]['yhat_lower']
        upper = forecast.iloc[-1]['yhat_upper']

        return forecast, df, currency_symbol, predicted, lower, upper
    except Exception as e:
        logger.error(f"Failed to generate forecast for {ticker}: {str(e)}")
        raise
