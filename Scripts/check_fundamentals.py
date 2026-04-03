import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

ticker = "323280"
date = "2026-03-19 00:00:00.000Z"
data = pb_utils.query_pb("stock_infos", filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
if data:
    item = data[0]
    print(f"--- Fundamental Data for {ticker} on {date} ---")
    print(f"PER: {item.get('PER')}")
    print(f"PBR: {item.get('PBR')}")
    print(f"EPS: {item.get('EPS')}")
    print(f"BPS: {item.get('BPS')}")
    print(f"DIV: {item.get('DIV')}")
else:
    print("No data found.")
