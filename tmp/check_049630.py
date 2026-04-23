import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_ticker():
    ticker = "052860"
    target_date = "2026-04-23"
    
    # 1. Check stock info
    stock = pb_utils.query_pb("stock_infos", filter_str=f'ticker="{ticker}"', limit=1)
    if stock:
        print(f"Ticker {ticker} Info: {stock[0].get('name')}")
    else:
        print(f"Ticker {ticker} not found in stock_infos")

    # 2. Check OHLCV for April 23rd
    filter_str = f'code="{ticker}" && date >= "{target_date} 00:00:00.000Z" && date <= "{target_date} 23:59:59.999Z"'
    ohlcv = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=1)
    
    if ohlcv:
        print(f"OHLCV for {ticker} on {target_date}:")
        print(json.dumps(ohlcv[0], indent=2))
    else:
        print(f"No OHLCV for {ticker} on {target_date} found.")

if __name__ == "__main__":
    check_ticker()
