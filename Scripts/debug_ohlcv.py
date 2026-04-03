import pandas as pd
from pb_utils import fetch_pb_ohlcv
ticker = '005930' # Samsung
df = fetch_pb_ohlcv(ticker, limit=10)
print(f"Ticker {ticker} data:")
print(df)
