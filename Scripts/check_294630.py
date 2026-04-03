import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-19 00:00:00.000Z"
ticker = "294630"
data = pb_utils.query_pb('news_analysis', filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
if data:
    print(f"--- Full Data for {ticker} on {date} ---")
    for k, v in data[0].items():
        print(f"{k}: {v}")
else:
    print(f"No entry found for ticker {ticker} on {date}")
