import pandas as pd
from typing import Optional

def get_recent_trend(df: pd.DataFrame) -> Optional[str]:
    if len(df) < 14:
        return None
    recent = df['y'].iloc[-7:].mean()
    previous = df['y'].iloc[-14:-7].mean()
    return "positive momentum" if recent > previous else "negative momentum"
