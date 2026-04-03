
from pykrx import stock
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")
print(f"Testing pykrx for {today}")

try:
    df = stock.get_market_ohlcv_by_ticker(today, market="KOSPI")
    if not df.empty:
        print("Success! First 5 rows:")
        print(df.head())
    else:
        print("Empty DataFrame. Maybe market is closed or blocked.")
except Exception as e:
    print(f"pykrx Failed: {e}")
