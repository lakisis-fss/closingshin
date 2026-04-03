import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

ticker = "323280" # 태성
dates = ["2026-03-19 00:00:00.000Z", "2026-03-20 00:00:00.000Z"]

print(f"--- Price Comparison for Ticker {ticker} ---")
for date in dates:
    print(f"\n[Date: {date}]")
    # Check vcp_reports
    vcp = pb_utils.query_pb("vcp_reports", filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
    if vcp:
        print(f"  vcp_reports price: {vcp[0].get('price')}")
    else:
        print(f"  vcp_reports: No record")

    # Check stock_infos
    info = pb_utils.query_pb("stock_infos", filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
    if info:
        print(f"  stock_infos close:  {info[0].get('close')}")
    else:
        print(f"  stock_infos: No record")
