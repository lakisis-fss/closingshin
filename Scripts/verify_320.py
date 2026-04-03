import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

ticker = "289080"
date = "2026-03-20 00:00:00.000Z"
data = pb_utils.query_pb('stock_infos', filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
print(f"--- Data Verification for {ticker} on {date} ---")
if data:
    print(f"Close: {data[0].get('close')}")
    print(f"Change %: {data[0].get('price_change_pct')}%")
else:
    print("No data found.")
