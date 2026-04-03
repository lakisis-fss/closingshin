import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-20 00:00:00.000Z"
data = pb_utils.query_pb('vcp_reports', filter_str=f'date="{date}"', limit=10)
print(f"--- VCP Reports for {date} ---")
if data:
    for item in data:
        print(f"Ticker: {item.get('ticker')}, Name: {item.get('name')}")
else:
    print("No VCP reports found for this date.")
