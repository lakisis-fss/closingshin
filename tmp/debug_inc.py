import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def find_ticker():
    # 1. Search in vcp_reports around April 2nd to find the exact name/ticker
    print("Searching for INC in vcp_reports...")
    recs = pb_utils.query_pb("vcp_reports", filter_str='name ~ "아이엔씨" || ticker ~ "아이엔씨"', limit=5)
    if not recs:
        # Try finding in stock_infos again with simplified search
        print("Not found in vcp_reports. Searching in stock_infos...")
        recs = pb_utils.query_pb("stock_infos", filter_str='name ~ "아이엔씨"', limit=5)
    
    if not recs:
        print("Still not found. Listing first 5 stock_infos to check data format:")
        debug_recs = pb_utils.query_pb("stock_infos", limit=5)
        for r in debug_recs:
            print(f"Ticker: {r.get('ticker')}, Name: {r.get('name')}")
        return

    for r in recs:
        ticker = r.get('ticker')
        name = r.get('name')
        print(f"Match Found: Ticker={ticker}, Name={name}")
        
        # 2. Check OHLCV for April 23rd
        target_date = "2026-04-23"
        filter_str = f'code="{ticker}" && date >= "{target_date} 00:00:00.000Z" && date <= "{target_date} 23:59:59.999Z"'
        ohlcv = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=1)
        
        if ohlcv:
            print(f"OHLCV for {target_date}:")
            print(json.dumps(ohlcv[0], indent=2))
        else:
            print(f"No OHLCV for {target_date} found for ticker {ticker}")

if __name__ == "__main__":
    find_ticker()
