import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-19 00:00:00.000Z"
tickers = ["831980", "323280", "253590"] # PSK, Taesung, Neosem
print(f"--- 3/19 vcp_reports Verification ---")
for t in tickers:
    data = pb_utils.query_pb("vcp_reports", filter_str=f'ticker="{t}" && date="{date}"', limit=1)
    if data:
        print(f"Ticker {t}: Price {data[0].get('price')}")
    else:
        print(f"Ticker {t}: No data")
