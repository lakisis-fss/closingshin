import os
import sys

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils
import json
from datetime import datetime

def check_stock_price(ticker, date_str):
    formatted_date_start = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 00:00:00.000Z"
    formatted_date_end = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 23:59:59.999Z"
    
    print(f"\n--- Checking market data for {ticker} on {date_str} ---")
    
    # Check ohlcv
    filter_str = f'code="{ticker}" && date >= "{formatted_date_start}" && date <= "{formatted_date_end}"'
    ohlcv_recs = pb_utils.query_pb('ohlcv', filter_str=filter_str)
    
    if ohlcv_recs:
        for rec in ohlcv_recs:
            print(f"Match: Date={rec.get('date')}, Open={rec.get('open')}, High={rec.get('high')}, Low={rec.get('low')}, Close={rec.get('close')}")
    else:
        print("No market records found for this date.")

if __name__ == "__main__":
    check_stock_price("420770", "20260320")
