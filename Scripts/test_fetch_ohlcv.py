from pb_utils import fetch_pb_ohlcv
import pandas as pd

def test_fetch_ohlcv():
    ticker = "006800"
    df = fetch_pb_ohlcv(ticker, limit=5)
    print("DataFrame for 006800:")
    print(df)
    print("\nColumns:", df.columns.tolist())
    if not df.empty:
        print("\nTail close:", df['close'].iloc[-1])

if __name__ == "__main__":
    test_fetch_ohlcv()
