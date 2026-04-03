import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from datetime import datetime

def check_date(dt_str):
    fmt = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
    filter_str = f'date >= "{fmt} 00:00:00Z" && date <= "{fmt} 23:59:59Z"'
    recs = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=5)
    print(f"Checking date: {fmt}")
    print(f"Found {len(recs)} records")
    for r in recs:
        print(f"  {r['date']} - {r['code']}")

def check_latest_samsung():
    recs = pb_utils.query_pb("ohlcv", filter_str='code="005930"', sort="-date", limit=5)
    print("\nLatest Samsung (005930) dates:")
    for r in recs:
        print(f"  {r['date']}")

if __name__ == "__main__":
    check_date("20260319")
    check_latest_samsung()
