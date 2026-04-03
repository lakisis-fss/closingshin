from pb_utils import fetch_pb_ohlcv
import pandas as pd

def check_df_cols():
    ticker = "078600"
    df = fetch_pb_ohlcv(ticker, limit=5)
    print("Columns:", df.columns.tolist())
    if not df.empty:
        print("\nLast row:")
        print(df.iloc[-1])

if __name__ == "__main__":
    check_df_cols()
