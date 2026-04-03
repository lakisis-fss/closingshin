
import pb_utils
import json
from datetime import datetime

def check_progress():
    date_str = "2026-03-23"
    filter_str = f'date >= "{date_str} 00:00:00.000Z" && date <= "{date_str} 23:59:59.999Z"'
    
    recs = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=5000)
    print(f"Synced records for {date_str}: {len(recs)}")
    
    # Check current time in log or something if 08_sync_market_data.py is finished
    # But for now, just the count is enough.

if __name__ == "__main__":
    check_progress()
