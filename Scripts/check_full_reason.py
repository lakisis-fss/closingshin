import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-19 00:00:00.000Z"
ticker = "294630"
data = pb_utils.query_pb('news_analysis', filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
if data:
    reason = data[0].get('reason')
    print(f"--- Full Reason for {ticker} on {date} ---")
    print(reason)
    print("-" * 30)
    print(f"Sentiment Score: {data[0].get('sentiment_score')}")
    print(f"Target Stock: '{data[0].get('target_stock')}'")
else:
    print("No data found.")
