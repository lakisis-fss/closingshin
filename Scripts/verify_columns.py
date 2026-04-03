from pykrx import stock
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")
print(f"Testing for date: {today}")

try:
    df = stock.get_market_trading_value_by_date(today, today, "KOSPI", detail=False)
    print("Columns:", list(df.columns))
    print("Raw Data (First Row):")
    print(df.iloc[0])
except Exception as e:
    print("Error:", e)
