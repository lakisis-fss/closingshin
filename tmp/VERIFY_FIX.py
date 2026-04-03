import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_collection(name, date_str):
    iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 00:00:00.000Z"
    print(f"--- Checking {name} for {iso_date} ---")
    try:
        recs = pb_utils.query_pb(name, filter_str=f'date="{iso_date}"', limit=100)
        print(f"  Count: {len(recs)}")
        if recs:
            tickers = [r.get('ticker') or r.get('code') for r in recs]
            duplicates = [t for t in set(tickers) if tickers.count(t) > 1]
            print(f"  Tickers: {tickers}")
            print(f"  Duplicates: {duplicates}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    date = "20260319"
    check_collection("vcp_reports", date)
    check_collection("stock_infos", date)
    check_collection("news", date)
    check_collection("news_analysis", date)
