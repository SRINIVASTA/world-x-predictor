import pandas as pd
from prophet import Prophet
import yfinance as yf
from config.base_settings import TIMEFRAME_PERIODS, get_currency_symbol
from config.logger_config import setup_logger

logger = setup_logger("forecasting_engine")

def make_forecast(ticker: str, timeframe: str, sentiment_score: float = 0.0):
    """
    Generates time-series price forecasts using Facebook Prophet, 
    dynamically skewing prediction intervals based on live macro news sentiment indicators.
    """
    logger.info(f"Generating forecast for {ticker} over {timeframe} with sentiment modifier: {sentiment_score:+.2f}")
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

        df = stock.history(period="5y")[["Close"]].reset_index()
        if df.empty:
            raise ValueError(f"No historical data found for ticker: {ticker}")
            
        df.columns = ["ds", "y"]
        df['ds'] = df['ds'].dt.tz_localize(None)

        model = Prophet(daily_seasonality=True)
        model.fit(df)

        periods = TIMEFRAME_PERIODS.get(timeframe, 90)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        # 📊 Dynamic Sentiment Interval Adjustment Matrix
        # A volatility scaler defines how heavily sentiment can shift the math model boundaries (10% max threshold here)
        volatility_multiplier = 0.10 
        sentiment_modifier = sentiment_score * volatility_multiplier

        predicted = forecast.iloc[-1]['yhat']
        
        # Apply structured skews to your time-series confidence bands
        raw_lower = forecast.iloc[-1]['yhat_lower']
        raw_upper = forecast.iloc[-1]['yhat_upper']
        
        # Bullish sentiment pushes both lines upward slightly; bearish sentiment pulls them down
        lower = raw_lower * (1.0 + sentiment_modifier)
        upper = raw_upper * (1.0 + sentiment_modifier)

        # Prevent statistical breakdown flips where lower crosses upper due to massive skews
        if lower > upper:
            lower, upper = upper, lower

        return forecast, df, currency_symbol, predicted, lower, upper
    except Exception as e:
        logger.error(f"Failed to generate forecast for {ticker}: {str(e)}")
        raise
