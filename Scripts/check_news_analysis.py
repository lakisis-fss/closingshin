import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

date = "2026-03-19 00:00:00.000Z"
target_stock = "서남"
# Try searching by name
data = pb_utils.query_pb('news_analysis', filter_str=f'target_stock="{target_stock}" && date="{date}"', limit=10)

print(f"--- News Analysis for {target_stock} on {date} ---")
if data:
    for item in data:
        print(f"ID: {item.get('id')}")
        print(f"Ticker: {item.get('ticker')}") # Check if ticker exists
        print(f"Name: {item.get('target_stock')}")
        print(f"Score: {item.get('sentiment_score')}")
        print(f"Reason: {item.get('reason')}")
        print("-" * 20)
else:
    print("Searching for all records on this date...")
    all_data = pb_utils.query_pb('news_analysis', filter_str=f'date="{date}"', limit=100)
    for item in all_data:
        t_stock = item.get('target_stock')
        ticker = item.get('ticker')
        reason = item.get('reason', '')[:50]
        print(f"ID: {item.get('id')} | Ticker: '{ticker}' | Name: '{t_stock}' | Reason: {reason}...")
