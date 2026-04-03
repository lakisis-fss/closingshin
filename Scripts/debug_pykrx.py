import os
import sys
from pykrx import stock
from datetime import datetime
import pandas as pd

def debug_fetch():
    TODAY = datetime.now().strftime("%Y%m%d")
    end_date = TODAY
    start_date = "20260101" # 충분히 긴 기간
    
    try:
        import FinanceDataReader as fdr
        print("\nTesting fdr.StockListing('KOSPI')...")
        df_fdr = fdr.StockListing('KOSPI')
        if df_fdr is not None and not df_fdr.empty:
            print("Success: fdr.StockListing worked")
            print("Columns:", df_fdr.columns.tolist())
            print(df_fdr.head(2))
        else:
            print("Error: fdr.StockListing returned empty")
    except Exception as e:
        print(f"Failed: fdr.StockListing - {e}")

if __name__ == "__main__":
    debug_fetch()
