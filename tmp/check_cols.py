import pb_utils
import pandas as pd
import sys
import os

# Add Scripts to sys.path
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

def check_ohlcv():
    ticker = "000270" # 기아
    df = pb_utils.fetch_pb_ohlcv(ticker, limit=10)
    if df is not None:
        print(f"Columns for {ticker}: {df.columns.tolist()}")
        # print(df.head(2))
    else:
        print("Failed to fetch OHLCV data.")

if __name__ == "__main__":
    check_ohlcv()
