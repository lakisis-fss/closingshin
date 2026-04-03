import sys
import os
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

print("--- Data Verification (V4: Close & Change %) ---")
for date in ["2026-03-19 00:00:00.000Z", "2026-03-20 00:00:00.000Z"]:
    data = pb_utils.query_pb('stock_infos', filter_str=f'ticker="294630" && date="{date}"', limit=1)
    if data:
        print(f"Date: {date}")
        print(f"  Ticker: {data[0].get('ticker')}")
        print(f"  Name:   {data[0].get('name')}")
        print(f"  Close:  {data[0].get('close')}")
        print(f"  Change %: {data[0].get('price_change_pct')}%")
    else:
        print(f"No data for {date}")
