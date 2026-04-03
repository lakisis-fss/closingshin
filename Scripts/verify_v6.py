import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-19 00:00:00.000Z"
ticker = "294630"
data = pb_utils.query_pb('news_analysis', filter_str=f'ticker="{ticker}" && date="{date}"', limit=5)
if data:
    print(f"--- AI Sentiment Verification (V6) for {ticker} ---")
    for i, item in enumerate(data):
        print(f"Record {i+1} (ID: {item.get('id')}):")
        print(f"  Target Stock: '{item.get('target_stock')}'")
        print(f"  Reason (First 100 char): {item.get('reason', '')[:100]}...")
        print(f"  Sentiment Score: {item.get('sentiment_score')}")
        print("-" * 20)
else:
    print("No data found for 294630 on 3/19.")
