# 🌾 Commodity Assets Lookup Directory
COMMODITIES_MAP = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "HG=F": "Copper",
    "PL=F": "Platinum",
    "CL=F": "Crude Oil",
    "BRN=F": "Brent Oil",
    "HO=F": "Heating Oil",
    "RB=F": "RBOB Gasoline"
}

# 🗓️ Extended Horizon Prediction Intervals 
TIMEFRAME_PERIODS = {
    '1 day': 1,
    '1 week': 7,
    '1 month': 30,
    '3 months': 90,
    '6 months': 180,
    '1 year': 365,
    '2 year': 730 
}

# 🌍 Global Currencies Visual Symbols Layout
CURRENCY_SYMBOLS = {
    "USD": "$",
    "INR": "₹",
    "GBP": "£",
    "GBX": "p",  # British Pence
    "EUR": "€",
    "CAD": "$",
    "AUD": "$",
    "NZD": "$",
    "JPY": "¥",
    "CNY": "¥",
    "HKD": "$",
    "SGD": "$",
    "CHF": "CHF",
    "KRW": "₩",
    "BRL": "R$"
}

def get_currency_symbol(currency_code: str) -> str:
    """
    Transforms traditional ISO text blocks into regional currency symbols.
    """
    if not currency_code:
        return "$"
    code_upper = currency_code.upper()
    return CURRENCY_SYMBOLS.get(code_upper, code_upper)
